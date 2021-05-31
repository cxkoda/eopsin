from model.candle import Candle, Interval
from model.pair import Pair
from service.dbservice import DBService
from exchange.exchange import ExchangeHandler, Order

import datetime
from typing import List
import binance


class BinanceHandler(ExchangeHandler):
    name = 'Binance'

    def __init__(self, dbservice: DBService, apiKey: str, apiSecret: str):
        super().__init__(dbservice)
        self.client = binance.Client(apiKey, apiSecret)

    def __del__(self):
        self.client.session.close()

    def convertIntervalString(self, interval: Interval) -> str:
        return interval.value

    def convertPairSymbol(self, pair: Pair) -> str:
        return pair.asset + pair.currency

    def convertDate(self, date: datetime) -> str:
        return datetime.strftime(date, '%Y-%m-%d %H:%M:%S')

    def getCandleFromData(self, pair: Pair, interval: Interval, data: list) -> Candle:
        candle = Candle(exchange=self.exchange, pair=pair, interval=interval,
                        openTime=datetime.datetime.fromtimestamp(data[0] / 1000),  # binance timestamps are given in ms
                        open=float(data[1]),
                        high=float(data[2]),
                        low=float(data[3]),
                        close=float(data[4]),
                        volume=float(data[5]),
                        closeTime=datetime.datetime.fromtimestamp(data[6] / 1000),
                        quoteAssetVolume=float(data[7]),
                        numberOfTrades=data[8],
                        takerBuyBaseAssetVolume=float(data[9]),
                        takerBuyQuoteAssetVolume=float(data[10]),
                        )
        return candle

    def getHistoricalKlinesFromServer(self, pair: Pair, interval: Interval, periodStart: datetime,
                                      periodEnd: datetime) -> List[Candle]:
        convertDate = lambda date: datetime.datetime.strftime(date, '%Y-%m-%d %H:%M:%S')
        candles = [self.getCandleFromData(pair, interval, candle) for candle in
                   self.client.get_historical_klines_generator(self.convertPairSymbol(pair),
                                                               self.convertIntervalString(interval),
                                                               convertDate(periodStart),
                                                               convertDate(periodEnd))]
        return candles

    def getAssetBalance(self, asset: str):
        pass

    def getPortfolio(self):
        pass

    def placeOrder(self, order: Order):
        pass

    def checkOrder(self, orderId):
        pass

    def cancelOrder(self, orderId):
        pass
