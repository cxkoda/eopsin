import datetime as dt
import logging
import os
import sys

import sqlalchemy as sql

import eopsin as eop

'''
In this example we will fetch 1-hour candles for a given time period from Binance and store it in a sqlite database.
'''

# Period (in local time) for which we want to get the candles
PERIOD_START = dt.datetime(2021, 1, 1, 0, 0)
PERIOD_END = dt.datetime(2021, 1, 2, 0, 0)

# Set up dan sqlite database
engine = sql.create_engine("sqlite:///example-db.sqlite", echo=False, future=True)
dbService = eop.DBService(engine)

# To enusre DB consistency, we have to use the DB-service to get a given pair
pair = dbService.getPair('BTC', 'USDT')

# Get binance api token from the environment ...
BINANCE_API_KEY = os.environ['BINANCE_TEST_API_KEY']
BINANCE_API_SECRET = os.environ['BINANCE_TEST_API_SECRET']
# ... and set up the exchange handler
binance = eop.BinanceHandler(dbService, BINANCE_API_KEY, BINANCE_API_SECRET)

# Set up a debug logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Get the candle data
# If the candles are not already in the database, they will be fetched from the exchange and stored automatically.
# Otherwise, the candles will just be loaded from the database and the instruction will return very quickly (e.g. execute the script twice)
candles = binance.getHistoricalKlines(pair, eop.Interval.HOUR_1, PERIOD_START, PERIOD_END)

for candle in candles:
    print(candle)
