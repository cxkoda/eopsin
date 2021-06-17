import copy
import datetime as dt
import itertools as it
from typing import List, Dict

import eopsin.model as m
import eopsin.util as util
from .exchange import ExchangeHandler


class ExchangeEmulator(ExchangeHandler):
    _exchangeHandler: ExchangeHandler
    _portfolio: Dict[str, float]

    class _Decorators:
        @classmethod
        def delegateToExchange(cls, fun):
            def delegatedFun(self, *args, **kwargs):
                return getattr(self._exchangeHandler, fun.__name__)(*args, **kwargs)

            return delegatedFun

    def __init__(self, exchange: ExchangeHandler, portfolio: Dict[str, float] = {},
                 now: dt.datetime = dt.datetime.now()):
        self.name = f'{exchange.name}-Emulator'
        super().__init__(exchange.dbservice)
        self._exchangeHandler = exchange
        self._portfolio = portfolio
        self._now = now.astimezone(dt.timezone.utc)
        self._orders = {}
        self._orderIdGenerator = it.count(1)

    @_Decorators.delegateToExchange
    def _getHistoricalKlinesFromServer(self, pair: m.Pair, interval: m.Interval, periodStart: dt.datetime,
                                       periodEnd: dt.datetime) -> List[m.Candle]:
        pass

    @_Decorators.delegateToExchange
    def getLastCompleteCandleBefore(self, pair: m.Pair, interval: m.Interval, date: dt.datetime) -> m.Candle:
        pass

    def getCurrentCourse(self, pair: m.Pair):
        ''' Defined to be the closing price of the last 1 minute candle '''
        return self._exchangeHandler.getLastCompleteCandleBefore(pair, m.Interval.MINUTE_1, self._now).close

    def getTime(self) -> dt.datetime:
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

        if order.volumeType == order.volumeType.ASSET:
            assetVolume = order.volume
            currencyVolume = order.volume * currentCourse
        else:
            assetVolume = order.volume / currentCourse
            currencyVolume = order.volume

        if order.side is m.OrderSide.SELL:
            balance = self.getAssetBalance(order.pair.asset)

            if assetVolume > balance:
                order.status = m.OrderStatus.REJECTED
                self.log.warning(
                    f'Rejecting order {order}: Not enough asset ({order.pair.asset}) - need: {assetVolume} but available: {balance}')
            else:
                self._portfolio[order.pair.asset] -= assetVolume
                self._portfolio[order.pair.currency] += currencyVolume
                order.status = m.OrderStatus.FILLED
        elif order.side is m.OrderSide.BUY:
            balance = self.getAssetBalance(order.pair.currency)
            if currencyVolume > balance:
                order.status = m.OrderStatus.REJECTED
                self.log.warning(
                    f'Rejecting order {order}: Not enough currency ({order.pair.currency}) - need: {currencyVolume} but available: {balance}')
            else:
                self._portfolio[order.pair.asset] += assetVolume
                self._portfolio[order.pair.currency] -= currencyVolume
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

    def eventLoop(self, tickwidth: dt.timedelta, terminate=lambda: False) -> None:
        while not terminate():
            self._now = util.floorDatetime(self._now, tickwidth) + tickwidth
            self._fireEvents(self._now)

    def _getBacktestTermination(self, periodEnd: dt.datetime):
        def terminate():
            return self.getTime() >= periodEnd

        return terminate

    def backtest(self, periodStart: dt.datetime, periodEnd: dt.datetime,
                 tickwidth: dt.timedelta = dt.timedelta(minutes=1)):
        self._now = periodStart
        self.eventLoop(tickwidth, terminate=self._getBacktestTermination(periodEnd))
