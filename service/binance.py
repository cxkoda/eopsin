from model.candle import Candle
from model.pair import Pair

import binance
import datetime
from sqlalchemy import and_


class BinanceService:
    def __init__(self, session, apiKey, apiSecret):
        self.client = binance.Client(apiKey, apiSecret)
        self.session = session

    @staticmethod
    def getPairSymbol(pair: Pair):
        assert (pair.exchange.name == 'Binance')
        return pair.asset + pair.currency

    @staticmethod
    def getCandleFromData(pair: Pair, interval, data):
        assert (pair.exchange.name == 'Binance')
        candle = Candle(pair=pair, interval=interval,
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

    def getHistoricalKlinesFromServer(self, pair: Pair, interval, periodStart: datetime.datetime,
                                      periodEnd: datetime.datetime):
        convertDate = lambda date: datetime.datetime.strftime(date, '%Y-%m-%d %H:%M:%S')
        candles = [self.getCandleFromData(pair, interval, candle) for candle in
                   self.client.get_historical_klines_generator(self.getPairSymbol(pair), interval,
                                                               convertDate(periodStart),
                                                               convertDate(periodEnd))]

        return candles

    def getHistoricalKlines(self, pair: Pair, interval, periodStart: datetime.datetime,
                            periodEnd: datetime.datetime):
        candles = self.session.query(Candle) \
            .filter(and_(Candle.pair_id == pair.id,
                         Candle.interval == interval,
                         Candle.openTime.between(periodStart, periodEnd))) \
            .order_by(Candle.openTime).all()

        if candles:
            return candles
        else:
            candles = self.getHistoricalKlinesFromServer(pair, interval, periodStart, periodEnd)
            for candle in candles:
                self.session.add(candle)
            return candles
