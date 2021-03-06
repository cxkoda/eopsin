import logging
from datetime import datetime, timezone
from typing import List, Tuple

import sqlalchemy as sql
import sqlalchemy.exc as exc
import sqlalchemy.orm as orm

import eopsin.model as m
import eopsin.util as util
from eopsin.model._sqlbase import Base

_logger = logging.getLogger(__name__)


class DBService:
    def __init__(self, engine):
        self.engine = engine
        Base.metadata.create_all(engine)

        Session = sql.orm.sessionmaker(bind=engine)
        self.session = Session()

    def addExchange(self, name: str) -> m.Exchange:
        exchange = m.Exchange(name=name)
        self.session.add(exchange)
        self.session.commit()

        return exchange

    def findExchange(self, name: str) -> m.Exchange:
        exchange = self.session.query(m.Exchange).filter(m.Exchange.name == name).first()
        return exchange

    def getExchange(self, name: str) -> m.Exchange:
        exchange = self.findExchange(name)
        if exchange:
            return exchange
        else:
            return self.addExchange(name)

    def addPair(self, pair: m.Pair):
        self.session.add(pair)
        self.session.commit()

    def findPair(self, asset: str, currency: str):
        return self.session.query(m.Pair).filter(sql.and_(
            m.Pair.asset == asset, m.Pair.currency == currency)).first()

    def getPair(self, asset: str, currency: str):
        pair = self.findPair(asset, currency)
        if pair is None:
            pair = m.Pair(asset=asset, currency=currency)
            self.addPair(pair)
        return pair

    def addCandle(self, candle: m.Candle):
        try:
            self.session.add(candle)
            self.session.commit()
        except sql.exc.IntegrityError:
            self.session.rollback()

    def addCandles(self, candles: List[m.Candle]):
        _logger.debug(f'Adding klines to the db: {candles}')
        for candle in candles:
            self.addCandle(candle)

    def findCandles(self, exchange: m.Exchange, pair: m.Pair, interval: m.Interval, periodStart: datetime,
                    periodEnd: datetime) -> List[m.Candle]:
        _logger.debug(f'Loading klines from the db: {pair} klines ({interval}) {exchange} for the period {periodStart} - {periodEnd}')
        return self.session.query(m.Candle) \
            .filter(sql.and_(m.Candle.exchange_id == exchange.id,
                             m.Candle.pair_id == pair.id,
                             m.Candle.interval == interval,
                             m.Candle.openTime >= periodStart,
                             m.Candle.closeTime <= periodEnd)) \
            .order_by(m.Candle.openTime).all()

    def findMissingCandlePeriods(self, exchange: m.Exchange, pair: m.Pair, interval: m.Interval, periodStart: datetime,
                                 periodEnd: datetime) -> \
            List[Tuple[datetime, datetime]]:
        _logger.debug(f'Looking for missing klines in the db: {pair} klines ({interval}) {exchange} for the period {periodStart} - {periodEnd}')
        periodStart = util.ceilDatetime(periodStart, interval.timedelta()).astimezone(timezone.utc)
        periodEnd = util.floorDatetime(periodEnd, interval.timedelta()).astimezone(timezone.utc)
        candles = self.session.query(m.Candle) \
            .filter(sql.and_(m.Candle.exchange_id == exchange.id,
                             m.Candle.pair_id == pair.id,
                             m.Candle.interval == interval,
                             m.Candle.openTime >= periodStart,
                             m.Candle.closeTime <= periodEnd)) \
            .options(sql.orm.load_only('openTime')) \
            .order_by(m.Candle.openTime)

        opens = [candle.openTime for candle in candles]

        missingPeriods = []
        currentBegin = None
        currentEnd = None

        for idx in range(int((periodEnd - periodStart) / interval.timedelta())):
            openTime = periodStart + idx * interval.timedelta()
            if openTime not in opens:
                if currentBegin is None:
                    currentBegin = openTime
                currentEnd = openTime + interval.timedelta()
            else:
                if currentEnd is not None:
                    missingPeriods.append([currentBegin, currentEnd])
                    currentBegin = currentEnd = None

        if currentEnd is not None:
            missingPeriods.append([currentBegin, currentEnd])

        return missingPeriods
