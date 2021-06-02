from model.exchange import Exchange
from model.pair import Pair
from model.candle import Candle, Interval
from service.util import ceilDatetime, floorDatetime
from model._sqlbase import Base

from sqlalchemy.orm import sessionmaker, load_only
from sqlalchemy import and_
from datetime import datetime
from typing import List, Tuple
from sqlalchemy.exc import IntegrityError


class DBService:
    def __init__(self, engine):
        self.engine = engine
        Base.metadata.create_all(engine)

        Session = sessionmaker(bind=engine)
        self.session = Session()

    def addExchange(self, name: str) -> Exchange:
        exchange = Exchange(name=name)
        self.session.add(exchange)
        self.session.commit()

        return exchange

    def findExchange(self, name: str) -> Exchange:
        exchange = self.session.query(Exchange).filter(Exchange.name == name).first()
        return exchange

    def getExchange(self, name: str) -> Exchange:
        exchange = self.findExchange(name)
        if exchange:
            return exchange
        else:
            return self.addExchange(name)

    def addPair(self, pair: Pair):
        self.session.add(pair)
        self.session.commit()

    def findPair(self, asset: str, currency: str):
        return self.session.query(Pair).filter(and_(
            Pair.asset == asset, Pair.currency == currency)).first()

    def getPair(self, asset: str, currency: str):
        pair = self.findPair(asset, currency)
        if pair is None:
            pair = Pair(asset=asset, currency=currency)
            self.addPair(pair)
        return pair

    def addCandle(self, candle: Candle):
        try:
            self.session.add(candle)
            self.session.commit()
        except IntegrityError:
            self.session.rollback()

    def addCandles(self, candles: List[Candle]):
        for candle in candles:
            self.addCandle(candle)

    def findCandles(self, exchange: Exchange, pair: Pair, interval: Interval, periodStart: datetime,
                    periodEnd: datetime) -> List[Candle]:
        return self.session.query(Candle) \
            .filter(and_(Candle.exchange_id == exchange.id,
                         Candle.pair_id == pair.id,
                         Candle.interval == interval,
                         Candle.openTime.between(periodStart, periodEnd))) \
            .order_by(Candle.openTime).all()

    def findMissingCandlePeriods(self, exchange: Exchange, pair: Pair, interval: Interval, periodStart: datetime,
                                 periodEnd: datetime) -> \
            List[Tuple[datetime, datetime]]:
        periodStart = ceilDatetime(periodStart, interval.timedelta())
        periodEnd = floorDatetime(periodEnd, interval.timedelta())
        candles = self.session.query(Candle) \
            .filter(and_(Candle.exchange_id == exchange.id,
                         Candle.pair_id == pair.id,
                         Candle.interval == interval,
                         Candle.openTime.between(periodStart, periodEnd))) \
            .options(load_only('openTime')) \
            .order_by(Candle.openTime)

        opens = [candle.openTime for candle in candles]

        missingPeriods = []
        currentBegin = None
        currentEnd = None

        for idx in range(int((periodEnd - periodStart) / interval.timedelta())):
            openTime = periodStart + idx * interval.timedelta()
            if openTime not in opens:
                if currentBegin is None:
                    currentBegin = openTime
                else:
                    currentEnd = openTime + interval.timedelta()
            else:
                if currentEnd is not None:
                    missingPeriods.append([currentBegin, currentEnd])
                    currentBegin = currentEnd = None

        if currentEnd is not None:
            missingPeriods.append([currentBegin, currentEnd])

        return missingPeriods
