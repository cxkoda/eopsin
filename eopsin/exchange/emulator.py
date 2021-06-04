import copy
import itertools as it
from datetime import datetime
from typing import List, Dict

import eopsin.model as m
from .exchange import ExchangeHandler


class ExchangeEmulator(ExchangeHandler):
    name = 'Emulator'
    _exchangeHandler: ExchangeHandler
    _portfolio: Dict[str, float]

    class _Decorators:
        @classmethod
        def delegateToExchange(cls, fun):
            def delegatedFun(self, *args, **kwargs):
                return getattr(self._exchangeHandler, fun.__name__)(*args, **kwargs)

            return delegatedFun

    def __init__(self, exchange: ExchangeHandler, portfolio: Dict[str, float] = {}, now: datetime = datetime.now()):

        super().__init__(exchange.dbservice)
        self._exchangeHandler = exchange
        self._portfolio = portfolio
        self._now = now
        self._orders = {}
        self._orderIdGenerator = it.count(1)

    @_Decorators.delegateToExchange
    def _getHistoricalKlinesFromServer(self, pair: m.Pair, interval: m.Interval, periodStart: datetime,
                                       periodEnd: datetime) -> List[m.Candle]:
        pass

    @_Decorators.delegateToExchange
    def getLastCompleteCandleBefore(self, pair: m.Pair, interval: m.Interval, date: datetime) -> m.Candle:
        pass

    def getCurrentCourse(self, pair: m.Pair):
        ''' Defined to be the closing price of the last 1 minute candle '''
        return self._exchangeHandler.getLastCompleteCandleBefore(pair, m.Interval.MINUTE_1, self._now).close

    def getTime(self) -> datetime:
        return self._now

    def getAssetBalance(self, asset: str):
        self._assureAssetInPortfolio(asset)
        return self._portfolio[asset]

    def getPortfolio(self):
        return copy.copy(self._portfolio)

    def _assureAssetInPortfolio(self, asset: str) -> None:
        if asset not in self._portfolio:
            self._portfolio[asset] = 0

    def _assurePairInPortfolio(self, pair: m.Pair) -> None:
        for asset in [pair.asset, pair.currency]:
            self._assureAssetInPortfolio(asset)

    def _processMarketOrder(self, order: m.MarketOrder) -> None:
        currentCourse = self.getCurrentCourse(order.pair)
        if order.side is m.OrderSide.SELL:
            if order.volume > self.getAssetBalance(order.pair.asset):
                order.status = m.OrderStatus.REJECTED
            else:
                assetValue = currentCourse * order.volume
                self._portfolio[order.pair.asset] -= order.volume
                self._portfolio[order.pair.currency] += assetValue
                order.status = m.OrderStatus.FILLED
        elif order.side is m.OrderSide.BUY:
            assetValue = currentCourse * order.volume
            if assetValue > self.getAssetBalance(order.pair.currency):
                order.status = m.OrderStatus.REJECTED
            else:
                assetValue = currentCourse * order.volume
                self._portfolio[order.pair.asset] += order.volume
                self._portfolio[order.pair.currency] -= assetValue
                order.status = m.OrderStatus.FILLED

    def placeOrder(self, order: m.Order) -> m.OrderId:
        self._assurePairInPortfolio(order.pair)
        order = copy.copy(order)
        orderIdentifier = m.OrderId(pair=order.pair, id=next(self._orderIdGenerator))
        self._orders[orderIdentifier.id] = order

        if isinstance(order, m.MarketOrder):
            self._processMarketOrder(order)
        else:
            raise ValueError(f"Order type unsupported: {type(order)}")

        return orderIdentifier

    def checkOrder(self, orderId: m.OrderId) -> m.OrderStatus:
        return self._orders[orderId.id].status

    def cancelOrder(self, orderId: m.OrderId) -> None:
        pass

    def getAllOrders(self, pair: m.Pair) -> List[m.Order]:
        pass

    def getAllOpenOrders(self, pair: m.Pair) -> List[m.Order]:
        pass
