import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Tuple, Dict

import eopsin.model as m
import eopsin.service as s
import eopsin.util as util


class NewCandleEvents(util.Events):

    @staticmethod
    def _getNewCandleEventName(interval: m.Interval):
        return f'onNewCandle_{interval.name}'

    def __init__(self):
        super().__init__(events=[NewCandleEvents._getNewCandleEventName(interval) for interval in m.Interval])

    def __getitem__(self, item):
        if isinstance(item, m.Interval):
            item = NewCandleEvents._getNewCandleEventName(item)
        return super().__getitem__(item)

    def __setitem__(self, item, value):
        if isinstance(item, m.Interval):
            item = NewCandleEvents._getNewCandleEventName(item)
        super().__setitem__(item, value)


class ExchangeHandler(ABC):
    name: str
    dbservice: s.DBService
    exchange: m.Exchange
    events: NewCandleEvents

    def __init__(self, dbservice: s.DBService):
        self.dbservice = dbservice
        self.exchange = dbservice.getExchange(self.name)
        self.events = NewCandleEvents()

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

    def _fireEvents(self, time: datetime) -> None:
        for interval in m.Interval:
            if util.floorDatetime(time, interval.timedelta()) == time:
                self.events[interval]()

    def eventLoop(self, tickwidth: timedelta, terminate=lambda: False) -> None:
        while not terminate():
            now = self.getTime()
            next = util.floorDatetime(now, tickwidth) + tickwidth
            delta = next - now
            time.sleep(delta.total_seconds())
            self._fireEvents(next)
