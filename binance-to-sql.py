import datetime
from sqlalchemy import create_engine

from service.binance import BinanceService
from service.dbservice import DBService

from model.candle import Interval

BINANCE_API_KEY = "xxxx"
BINANCE_API_SECRET = "xxxx"

PERIOD_START = "2021-01-01 00:00:00"
PERIOD_END = "2021-04-20 23:59:59"

engine = create_engine("sqlite:///foo.sqlite", echo=False, future=True)
dbService = DBService(engine)

pair = dbService.getPair('BTC', 'USDT', 'Binance')
print(pair)

binance = BinanceService(dbService, BINANCE_API_KEY, BINANCE_API_SECRET)
getDatetime = lambda date: datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
candles = binance.getHistoricalKlines(pair, Interval.HOUR_1, getDatetime(PERIOD_START), getDatetime(PERIOD_END))

print(candles)

dbService.session.commit()
