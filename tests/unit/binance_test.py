import datetime
import os
import unittest

from sqlalchemy import create_engine

from exchange.binance import BinanceHandler
from exchange.exchange import MarketOrder, OrderSide
from model.candle import Interval
from service.dbservice import DBService


class TestBinance(unittest.TestCase):

    def setUp(self) -> None:
        engine = create_engine("sqlite://", echo=False, future=True)
        self.dbService = DBService(engine)
        self.BINANCE_API_KEY = os.environ['BINANCE_TEST_API_KEY']
        self.BINANCE_API_SECRET = os.environ['BINANCE_TEST_API_SECRET']
        self.binance = BinanceHandler(self.dbService, self.BINANCE_API_KEY, self.BINANCE_API_SECRET, testnet=True)

    def test_connection(self):
        self.binance.client.ping()

    def test_getKlines(self):
        # API issue: Klines are not available on the testnet -> switching to normal server
        self.binance = BinanceHandler(self.dbService, self.BINANCE_API_KEY, self.BINANCE_API_SECRET)

        PERIOD_START = datetime.datetime(2021, 1, 2, 0, 0, 0) - datetime.timedelta(seconds=10)
        PERIOD_END = datetime.datetime(2021, 1, 10, 23, 59, 59)
        pair = self.dbService.getPair('BTC', 'USDT')
        candles = self.binance.getHistoricalKlines(pair, Interval.HOUR_1, PERIOD_START, PERIOD_END)
        self.assertEqual(216, len(candles))

        PERIOD_START = datetime.datetime(2021, 1, 3, 0, 0, 0)
        PERIOD_END = datetime.datetime(2021, 1, 13, 23, 59, 59)
        candles = self.binance.getHistoricalKlines(pair, Interval.HOUR_1, PERIOD_START, PERIOD_END)
        self.assertEqual(264, len(candles))

        PERIOD_START = datetime.datetime(2021, 1, 2, 0, 0, 0)
        candles = self.binance.getHistoricalKlines(pair, Interval.HOUR_1, PERIOD_START, PERIOD_END)
        self.assertEqual(288, len(candles))

    def test_portfolio(self):
        portfolio = self.binance.getPortfolio()
        self.assertEqual(portfolio['ETH'], self.binance.getAssetBalance('ETH'))

    def test_marketOrder(self):
        VOLUME = 1e-3

        before = self.binance.getAssetBalance('BTC')
        pair = self.dbService.getPair('BTC', 'USDT')
        order = MarketOrder(pair, OrderSide.SELL, VOLUME)
        orderId = self.binance.placeOrder(order)
        after = self.binance.getAssetBalance('BTC')
        # This causes a problem in the CI, where multiple orders are made simultaneously.
        # self.assertAlmostEqual(VOLUME, before - after, 4)

        self.assertEqual(self.binance.checkOrder(orderId)['status'], 'FILLED')


if __name__ == '__main__':
    unittest.main()
