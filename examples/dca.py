import datetime as dt
import logging
import os
import sys

import sqlalchemy as sql

import eopsin as eop

# Set up a debug logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Period (in local time) for which we want to get the candles
PERIOD_START = dt.datetime(2021, 1, 1, 0, 0, tzinfo=dt.timezone.utc)
PERIOD_END = dt.datetime(2021, 6, 1, 0, 0, tzinfo=dt.timezone.utc)

# Set up dan sqlite database
engine = sql.create_engine("sqlite:///backtest-db.sqlite", echo=False, future=True)
dbService = eop.DBService(engine)

# To enusre DB consistency, we have to use the DB-service to get a given pair
pair = dbService.getPair('BTC', 'USDT')

# Get binance api token from the environment ...
BINANCE_API_KEY = os.environ['BINANCE_TEST_API_KEY']
BINANCE_API_SECRET = os.environ['BINANCE_TEST_API_SECRET']
# ... and set up the exchange handler
binance = eop.BinanceHandler(dbService, BINANCE_API_KEY, BINANCE_API_SECRET, testnet=True)
emulator = eop.ExchangeEmulator(binance, portfolio={'USDT': 100})


class DCAStrategy(eop.Strategy):
    def __init__(self, exchange: eop.ExchangeHandler, pair: eop.Pair, interval: dt.timedelta, fraction):
        super().__init__(self.__class__.__name__)
        self.exchange = exchange
        self.pair = pair
        self.interval = interval

        balance = self.exchange.getAssetBalance(pair.currency)
        self.dcaVolume = balance * fraction
        self.lastBuy = None
        self.exchange.events[eop.Interval.DAY_1] += self.buy

    def buy(self):
        if self.exchange.getAssetBalance(pair.currency) > self.dcaVolume:
            order = eop.MarketOrder.newBuy(self.pair, self.dcaVolume, eop.VolumeType.CURRENCY)
            orderId = self.exchange.placeOrder(order)
            info = self.exchange.checkOrder(orderId)
            self.log.info(f'Placed order: {info}')


dca = DCAStrategy(emulator, pair, dt.timedelta(days=2), 0.02)

emulator.backtest(PERIOD_START, PERIOD_END, tickwidth=dt.timedelta(days=1))

print(emulator.getPortfolio())
