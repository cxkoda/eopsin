from model.candle import Candle, Interval
from model.pair import Pair
from service.dbservice import DBService

import binance
import datetime
from sqlalchemy import and_
from typing import List


class BinanceService:
    def __init__(self, dbService: DBService, apiKey: str, apiSecret: str):
        self.client = binance.Client(apiKey, apiSecret)
        self.session = dbService.session

    @staticmethod
    def getIntervalString(interval: Interval) -> str:
        return interval.value

    @staticmethod
    def getPairSymbol(pair: Pair) -> str:
        assert (pair.exchange.name == 'Binance')
        return pair.asset + pair.currency

    @staticmethod
    def getCandleFromData(pair: Pair, interval: Interval, data: list) -> Candle:
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

    def getHistoricalKlinesFromServer(self, pair: Pair, interval: Interval, periodStart: datetime.datetime,
                                      periodEnd: datetime.datetime) -> List[Candle]:
        convertDate = lambda date: datetime.datetime.strftime(date, '%Y-%m-%d %H:%M:%S')
        candles = [self.getCandleFromData(pair, interval, candle) for candle in
                   self.client.get_historical_klines_generator(self.getPairSymbol(pair),
                                                               self.getIntervalString(interval),
                                                               convertDate(periodStart),
                                                               convertDate(periodEnd))]

        return candles

    def getHistoricalKlines(self, pair: Pair, interval: Interval, periodStart: datetime.datetime,
                            periodEnd: datetime.datetime) -> List[Candle]:
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
