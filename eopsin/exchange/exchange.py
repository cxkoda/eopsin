from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Tuple, Dict

import eopsin.model as m
import eopsin.service as s


class ExchangeHandler(ABC):
    name: str
    dbservice: s.DBService
    exchange: m.Exchange

    def __init__(self, dbservice: s.DBService):
        self.dbservice = dbservice
        self.exchange = dbservice.getExchange(self.name)

    @abstractmethod
    def _getHistoricalKlinesFromServer(self, pair: m.Pair, interval: m.Interval, periodStart: datetime,
                                       periodEnd: datetime) -> List[m.Candle]:
        pass

    def _fetchMissingHistoricalKlines(self, pair: m.Pair, interval: m.Interval,
                                      missingPeriods: List[Tuple[datetime, datetime]]) -> None:
        for periodStart, periodEnd, in missingPeriods:
            candles = self._getHistoricalKlinesFromServer(pair, interval, periodStart, periodEnd)
            self.dbservice.addCandles(candles)

    def getHistoricalKlines(self, pair: m.Pair, interval: m.Interval, periodStart: datetime, periodEnd: datetime) -> \
            List[m.Candle]:
        missingPeriods = self.dbservice.findMissingCandlePeriods(self.exchange, pair, interval, periodStart, periodEnd)
        if missingPeriods:
            self._fetchMissingHistoricalKlines(pair, interval, missingPeriods)
            return self.getHistoricalKlines(pair, interval, periodStart, periodEnd)
        else:
            return self.dbservice.findCandles(self.exchange, pair, interval, periodStart, periodEnd)

    @abstractmethod
    def getLastCompleteCandleBefore(self, pair: m.Pair, interval: m.Interval, date: datetime) -> m.Candle:
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
    def placeOrder(self, order: m.Order) -> m.OrderId:
        pass

    # Check an exchange order status
    @abstractmethod
    def checkOrder(self, orderId: m.OrderId) -> m.OrderStatus:
        pass

    # Cancel an exchange order
    @abstractmethod
    def cancelOrder(self, orderId: m.OrderId) -> None:
        pass

    @abstractmethod
    def getAllOrders(self, pair: m.Pair) -> List[m.Order]:
        pass

    @abstractmethod
    def getAllOpenOrders(self, pair: m.Pair) -> List[m.Order]:
        pass
