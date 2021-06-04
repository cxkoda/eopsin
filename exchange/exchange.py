from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum, unique
from typing import List, Tuple, Dict

import model.exchange
from model.candle import Candle, Interval
from model.pair import Pair
from service.dbservice import DBService


@unique
class OrderSide(Enum):
    BUY = 1
    SELL = 2


@unique
class OrderStatus(Enum):
    NEW = 1
    PARTIALLY_FILLED = 2
    FILLED = 3
    CANCELED = 4
    PENDING_CANCEL = 5
    REJECTED = 6
    EXPIRED = 7


class OrderId:
    pair: Pair
    id: int

    def __init__(self, pair: Pair, id: int):
        self.pair = pair
        self.id = id

    def __repr__(self):
        return f'<OrderId(pair={self.pair}, id={self.id}>'


class Order:
    pair: Pair
    status: OrderStatus


class MarketOrder(Order):
    side: OrderSide
    volume: float

    def __init__(self, pair: Pair, side: OrderSide, volume: float, status: OrderStatus = OrderStatus.NEW):
        self.pair = pair
        self.side = side
        self.volume = volume
        self.status = status

    @classmethod
    def newSell(cls, pair: Pair, volume: float):
        return cls(pair, OrderSide.SELL, volume)

    @classmethod
    def newBuy(cls, pair: Pair, volume: float):
        return cls(pair, OrderSide.BUY, volume)


class LimitOrder(Order):
    side: OrderSide
    volume: float
    price: float

    def __init__(self, pair: Pair, side: OrderSide, volume: float, price: float, status: OrderStatus = OrderStatus.NEW):
        self.pair = pair
        self.side = side
        self.volume = volume
        self.price = price
        self.status = status


class ExchangeHandler(ABC):
    name: str
    dbservice: DBService
    exchange: model.exchange.Exchange

    def __init__(self, dbservice: DBService):
        self.dbservice = dbservice
        self.exchange = dbservice.getExchange(self.name)

    @abstractmethod
    def _getHistoricalKlinesFromServer(self, pair: Pair, interval: Interval, periodStart: datetime,
                                       periodEnd: datetime) -> List[Candle]:
        pass

    def _fetchMissingHistoricalKlines(self, pair: Pair, interval: Interval,
                                      missingPeriods: List[Tuple[datetime, datetime]]) -> None:
        for periodStart, periodEnd, in missingPeriods:
            candles = self._getHistoricalKlinesFromServer(pair, interval, periodStart, periodEnd)
            self.dbservice.addCandles(candles)

    def getHistoricalKlines(self, pair: Pair, interval: Interval, periodStart: datetime, periodEnd: datetime) -> List[
        Candle]:
        missingPeriods = self.dbservice.findMissingCandlePeriods(self.exchange, pair, interval, periodStart, periodEnd)
        if missingPeriods:
            self._fetchMissingHistoricalKlines(pair, interval, missingPeriods)
            return self.getHistoricalKlines(pair, interval, periodStart, periodEnd)
        else:
            return self.dbservice.findCandles(self.exchange, pair, interval, periodStart, periodEnd)

    @abstractmethod
    def getLastCompleteCandleBefore(self, pair: Pair, interval: Interval, date: datetime) -> Candle:
        pass

    @abstractmethod
    def getTime(self) -> datetime:
        pass

    @abstractmethod
    def getPortfolio(self) -> Dict[str, float]:
        pass

    # Get balance for a given asset
    @abstractmethod
    def getAssetBalance(self, asset: str) -> float:
        pass

    # Create an exchange order
    @abstractmethod
    def placeOrder(self, order: Order) -> OrderId:
        pass

    # Check an exchange order status
    @abstractmethod
    def checkOrder(self, orderId) -> OrderStatus:
        pass

    # Cancel an exchange order
    @abstractmethod
    def cancelOrder(self, orderId):
        pass

    @abstractmethod
    def getAllOrders(self, pair: Pair) -> List[Order]:
        pass

    @abstractmethod
    def getAllOpenOrders(self, pair: Pair) -> List[Order]:
        pass
