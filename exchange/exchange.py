from model.pair import Pair
from model.candle import Candle, Interval
from service.dbservice import DBService
import model.exchange

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List

from enum import Enum, unique


@unique
class OrderSide(Enum):
    BUY = 1
    SELL = 2


class Order:
    pair: Pair


class MarketOrder(Order):
    side: OrderSide
    volume: float

    def __init__(self, pair: Pair, side: OrderSide, volume: float):
        self.pair = pair
        self.side = side
        self.volume = volume


class LimitOrder(Order):
    side: OrderSide
    volume: float
    price: float

    def __init__(self, pair: Pair, side: OrderSide, volume: float, price: float):
        self.pair = pair
        self.side = side
        self.volume = volume
        self.price = price


class OrderId:
    pair: Pair
    id: int

    def __init__(self, pair: Pair, id: int):
        self.pair = pair
        self.id = id

    def __repr__(self):
        return f'<OrderId(pair={self.pair}, id={self.id}>'


class ExchangeHandler(ABC):
    name: str
    dbservice: DBService
    exchange: model.exchange.Exchange

    def __init__(self, dbservice: DBService):
        self.dbservice = dbservice
        self.exchange = dbservice.getExchange(self.name)

    @abstractmethod
    def _convertIntervalString(self, interval: Interval) -> str:
        return interval.value

    @abstractmethod
    def _convertPairSymbol(self, pair: Pair) -> str:
        return pair.asset + pair.currency

    @abstractmethod
    def _convertDate(self, date: datetime) -> str:
        return datetime.strftime(date, '%Y-%m-%d %H:%M:%S')

    @abstractmethod
    def _getHistoricalKlinesFromServer(self, pair: Pair, interval: Interval, periodStart: datetime,
                                       periodEnd: datetime) -> List[Candle]:
        pass

    def getHistoricalKlines(self, pair: Pair, interval: Interval, periodStart: datetime, periodEnd: datetime) -> List[
        Candle]:
        # missingPeriods = self.dbservice.findMissingCandlePeriods(self.exchange, pair, interval, periodStart, periodEnd)
        candles = self.dbservice.findCandles(self.exchange, pair, interval, periodStart, periodEnd)

        if candles:
            return candles
        else:
            candles = self._getHistoricalKlinesFromServer(pair, interval, periodStart, periodEnd)
            self.dbservice.addCandles(candles)
            return candles

    @abstractmethod
    def getPortfolio(self):
        pass

    # Get balance for a given asset
    @abstractmethod
    def getAssetBalance(self, asset: str):
        pass

    # Create an exchange order
    @abstractmethod
    def placeOrder(self, order: Order):
        pass

    # Check an exchange order status
    @abstractmethod
    def checkOrder(self, orderId):
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
