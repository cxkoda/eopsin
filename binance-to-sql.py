import datetime

import sqlalchemy as sql

import eopsin as eop

BINANCE_API_KEY = "xxxx"
BINANCE_API_SECRET = "xxxx"

PERIOD_START = "2021-01-01 00:00:00"
PERIOD_END = "2021-01-02 00:00:00"

engine = sql.create_engine("sqlite:///foo.sqlite", echo=False, future=True)
dbService = eop.DBService(engine)

pair = dbService.getPair('BTC', 'USDT')
print(pair)

binance = eop.BinanceHandler(dbService, BINANCE_API_KEY, BINANCE_API_SECRET)
getDatetime = lambda date: datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
candles = binance.getHistoricalKlines(pair, eop.Interval.MINUTE_1, getDatetime(PERIOD_START), getDatetime(PERIOD_END))

print(candles)

dbService.session.commit()
