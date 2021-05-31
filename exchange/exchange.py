from model.pair import Pair
from model.candle import Candle, Interval
from service.dbservice import DBService
import model.exchange

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List


class Order:
    pass


class ExchangeHandler(ABC):
    name: str
    dbservice: DBService
    exchange: model.exchange.Exchange

    def __init__(self, dbservice: DBService):
        self.dbservice = dbservice
        self.exchange = dbservice.getExchange(self.name)

    @abstractmethod
    def convertIntervalString(self, interval: Interval) -> str:
        return interval.value

    @abstractmethod
    def convertPairSymbol(self, pair: Pair) -> str:
        return pair.asset + pair.currency

    @abstractmethod
    def convertDate(self, date: datetime) -> str:
        return datetime.strftime(date, '%Y-%m-%d %H:%M:%S')

    @abstractmethod
    def getHistoricalKlinesFromServer(self, pair: Pair, interval: Interval, periodStart: datetime,
                                      periodEnd: datetime) -> List[Candle]:
        pass

    def getHistoricalKlines(self, pair: Pair, interval: Interval, periodStart: datetime, periodEnd: datetime) -> List[
        Candle]:
        missingPeriods = self.dbservice.findMissingCandlePeriods(self.exchange, pair, interval, periodStart, periodEnd)
        candles = self.dbservice.findCandles(self.exchange, pair, interval, periodStart, periodEnd)

        if candles:
            return candles
        else:
            candles = self.getHistoricalKlinesFromServer(pair, interval, periodStart, periodEnd)
            self.dbservice.addCandles(candles)
            return candles

    # Get balance for a given asset
    @abstractmethod
    def getAssetBalance(self, asset: str):
        pass

    @abstractmethod
    def getPortfolio(self):
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
