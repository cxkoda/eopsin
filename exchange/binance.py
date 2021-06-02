from datetime import datetime
from typing import List

import numpy as np

import binance
from exchange.exchange import ExchangeHandler, Order, LimitOrder, OrderSide, MarketOrder, OrderId
from model.candle import Candle, Interval
from model.pair import Pair
from service.dbservice import DBService
from service.util import ceilDatetime, floorDatetime


class BinanceHandler(ExchangeHandler):
    name = 'Binance'

    def __init__(self, dbservice: DBService, apiKey: str, apiSecret: str, **kwargs):
        super().__init__(dbservice)
        self.client = binance.Client(apiKey, apiSecret, **kwargs)

    def __del__(self):
        self.client.session.close()

    def _convertIntervalString(self, interval: Interval) -> str:
        return interval.value

    def _convertPairSymbol(self, pair: Pair) -> str:
        return pair.asset + pair.currency

    def _convertDate(self, date: datetime) -> str:
        return datetime.strftime(date, '%Y-%m-%d %H:%M:%S')

    def getCandleFromData(self, pair: Pair, interval: Interval, data: list) -> Candle:
        candle = Candle(exchange=self.exchange, pair=pair, interval=interval,
                        openTime=datetime.fromtimestamp(data[0] / 1000),  # binance timestamps are given in ms
                        open=float(data[1]),
                        high=float(data[2]),
                        low=float(data[3]),
                        close=float(data[4]),
                        volume=float(data[5]),
                        closeTime=datetime.fromtimestamp(data[6] / 1000),
                        quoteAssetVolume=float(data[7]),
                        numberOfTrades=data[8],
                        takerBuyBaseAssetVolume=float(data[9]),
                        takerBuyQuoteAssetVolume=float(data[10]),
                        )
        return candle

    def _getHistoricalKlinesFromServer(self, pair: Pair, interval: Interval, periodStart: datetime,
                                       periodEnd: datetime) -> List[Candle]:
        periodStart = ceilDatetime(periodStart, interval.timedelta())
        periodEnd = floorDatetime(periodEnd, interval.timedelta())
        candles = [self.getCandleFromData(pair, interval, candle) for candle in
                   self.client.get_historical_klines(self._convertPairSymbol(pair),
                                                     self._convertIntervalString(interval),
                                                     # shift by one to somehow get the right klines
                                                     self._convertDate(periodStart - interval.timedelta()),
                                                     self._convertDate(periodEnd - interval.timedelta()))]
        return candles

    def getAssetBalance(self, asset: str):
        info = self.client.get_asset_balance(asset=asset)
        return float(info['free'])

    def getPortfolio(self):
        info = self.client.get_account()
        portfolio = {entry['asset']: float(entry['free']) for entry in info['balances']}
        return portfolio

    def placeOrder(self, order: Order):
        symbol = self._convertPairSymbol(order.pair)
        getStr = lambda flt: np.format_float_positional(flt, trim='-')

        if isinstance(order, LimitOrder):
            if order.side is OrderSide.SELL:
                info = self.client.order_limit_sell(symbol=symbol, quantity=getStr(order.volume),
                                                    price=getStr(order.price))
            elif order.side is OrderSide.BUY:
                info = self.client.order_limit_buy(symbol=symbol, quantity=getStr(order.volume),
                                                   price=getStr(order.price))
            else:
                raise ValueError(f"Unknown order side: {order.side.name}")
        elif isinstance(order, MarketOrder):
            if order.side is OrderSide.SELL:
                info = self.client.order_market_sell(symbol=symbol, quantity=getStr(order.volume))
            elif order.side is OrderSide.BUY:
                info = self.client.order_market_buy(symbol=symbol, quantity=getStr(order.volume))
            else:
                raise ValueError(f"Unknown order side: {order.side.name}")
        else:
            raise ValueError(f"Unknown order type: {type(order)}")

        return OrderId(pair=order.pair, id=info['orderId'])

    def checkOrder(self, orderId: OrderId):
        return self.client.get_order(symbol=self._convertPairSymbol(orderId.pair), orderId=str(orderId.id))

    def cancelOrder(self, orderId: OrderId):
        pass

    def getAllOrders(self, pair: Pair):
        return self.client.get_all_orders(symbol=self._convertPairSymbol(pair))

    def getAllOpenOrders(self, pair: Pair) -> List[Order]:
        return self.client.get_open_orders(symbol=self._convertPairSymbol(pair))
