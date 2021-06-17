from datetime import datetime, timezone
from typing import List

import binance
import numpy as np

import eopsin.model as m
import eopsin.service as s
import eopsin.util as util
from .exchange import ExchangeHandler


class BinanceHandler(ExchangeHandler):
    name = 'Binance'

    def __init__(self, dbservice: s.DBService, apiKey: str, apiSecret: str, **kwargs):
        super().__init__(dbservice)
        self.client = binance.Client(apiKey, apiSecret, **kwargs)

    def __del__(self):
        self.client.session.close()

    def _convertIntervalString(self, interval: m.Interval) -> str:
        return interval.value

    def _convertPairSymbol(self, pair: m.Pair) -> str:
        return pair.asset + pair.currency

    def _convertDate(self, date: datetime) -> int:
        return int(date.timestamp() * 1000)  # in milliseconds

    def _convertTimestamp(self, timestamp: int) -> datetime:
        # binance timestamps are given in ms
        return datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc)

    def _getCandleFromData(self, pair: m.Pair, interval: m.Interval, data: list) -> m.Candle:
        candle = m.Candle(exchange=self.exchange, pair=pair, interval=interval,
                          openTime=self._convertTimestamp(data[0]),
                          open=float(data[1]),
                          high=float(data[2]),
                          low=float(data[3]),
                          close=float(data[4]),
                          volume=float(data[5]),
                          closeTime=self._convertTimestamp(data[6]),
                          quoteAssetVolume=float(data[7]),
                          numberOfTrades=data[8],
                          takerBuyBaseAssetVolume=float(data[9]),
                          takerBuyQuoteAssetVolume=float(data[10]),
                          )
        return candle

    def getTime(self) -> datetime:
        response = self.client.get_server_time()
        timestamp = float(response['serverTime'])  # timestamp is in milliseconds
        return datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc)

    def _getHistoricalKlinesFromServer(self, pair: m.Pair, interval: m.Interval, periodStart: datetime,
                                       periodEnd: datetime) -> List[m.Candle]:
        periodStart = util.ceilDatetime(periodStart, interval.timedelta(), tz=timezone.utc).astimezone(timezone.utc)
        periodEnd = util.floorDatetime(periodEnd, interval.timedelta(), tz=timezone.utc).astimezone(timezone.utc)
        candles = [self._getCandleFromData(pair, interval, candle) for candle in
                   self.client.get_historical_klines(self._convertPairSymbol(pair),
                                                     self._convertIntervalString(interval),
                                                     # shift by one to somehow get the right klines
                                                     self._convertDate(periodStart - interval.timedelta()),
                                                     self._convertDate(periodEnd))]
        return candles

    def getLastCompleteCandleBefore(self, pair: m.Pair, interval: m.Interval, date: datetime) -> m.Candle:
        begin = util.floorDatetime(date, interval.timedelta()) - interval.timedelta()
        candles = self.getHistoricalKlines(pair, interval, begin, date)
        return candles[0]

    def getAssetBalance(self, asset: str):
        info = self.client.get_asset_balance(asset=asset)
        return float(info['free'])

    def getPortfolio(self):
        info = self.client.get_account()
        portfolio = {entry['asset']: float(entry['free']) for entry in info['balances']}
        return portfolio

    def _processMarketOrder(self, order: m.MarketOrder) -> dict:
        getStr = lambda flt: np.format_float_positional(flt, trim='-')

        data = {}
        data['symbol'] = self._convertPairSymbol(order.pair)
        if order.volumeType == order.volumeType.ASSET:
            data['quantity'] = getStr(order.volume)
        else:
            data['quoteOrderQty'] = getStr(order.volume)

        if order.side is m.OrderSide.SELL:
            info = self.client.order_market_sell(**data)
        elif order.side is m.OrderSide.BUY:
            info = self.client.order_market_buy(**data)
        else:
            raise ValueError(f"Unknown order side: {order.side.name}")

        return info

    def placeOrder(self, order: m.Order) -> m.OrderId:
        symbol = self._convertPairSymbol(order.pair)
        getStr = lambda flt: np.format_float_positional(flt, trim='-')

        if isinstance(order, m.LimitOrder):
            if order.side is m.OrderSide.SELL:
                info = self.client.order_limit_sell(symbol=symbol, quantity=getStr(order.volume),
                                                    price=getStr(order.price))
            elif order.side is m.OrderSide.BUY:
                info = self.client.order_limit_buy(symbol=symbol, quantity=getStr(order.volume),
                                                   price=getStr(order.price))
            else:
                raise ValueError(f"Unknown order side: {order.side.name}")
        elif isinstance(order, m.MarketOrder):
            info = self._processMarketOrder(order)
        else:
            raise ValueError(f"Unknown order type: {type(order)}")

        self.log.debug(f'Placing order: {order} returned {info}')

        return m.OrderId(pair=order.pair, id=info['orderId'])

    def checkOrder(self, orderId: m.OrderId) -> m.OrderStatus:
        response = self.client.get_order(symbol=self._convertPairSymbol(orderId.pair), orderId=str(orderId.id))
        status = response['status']
        return m.OrderStatus[status]

    def getInfo(self, orderId: m.OrderId) -> m.OrderInfo:
        res = self.client.get_order(symbol=self._convertPairSymbol(orderId.pair), orderId=str(orderId.id))
        info = m.OrderInfo(pair=orderId.pair, orderId=res['orderId'],
                           time=self._convertTimestamp(res['time']),
                           orderedVolume=float(res['origQty']),
                           filledVolume=float(res['executedQty']),
                           filledCurrencyVolume=float(res['cummulativeQuoteQty']),
                           status=m.OrderStatus[res['status']],
                           type=res['type'],
                           side=m.OrderSide[res['side']],
                           )
        return info

    def cancelOrder(self, orderId: m.OrderId):
        pass

    def getAllOrders(self, pair: m.Pair):
        return self.client.get_all_orders(symbol=self._convertPairSymbol(pair))

    def getAllOpenOrders(self, pair: m.Pair) -> List[m.Order]:
        return self.client.get_open_orders(symbol=self._convertPairSymbol(pair))
