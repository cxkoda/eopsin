import datetime
import unittest
import os

from sqlalchemy import create_engine
from service.dbservice import DBService
from model.candle import Candle, Interval
from exchange.binance import BinanceHandler
from exchange.exchange import LimitOrder, MarketOrder, OrderSide
import time

getDatetime = lambda date: datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')


class TestBinance(unittest.TestCase):

    def setUp(self) -> None:
        engine = create_engine("sqlite://", echo=False, future=True)
        self.dbService = DBService(engine)
        BINANCE_API_KEY = os.environ['BINANCE_TEST_API_KEY']
        BINANCE_API_SECRET = os.environ['BINANCE_TEST_API_SECRET']
        self.binance = BinanceHandler(self.dbService, BINANCE_API_KEY, BINANCE_API_SECRET, testnet=True)

    def test_connection(self):
        self.binance.client.ping()

    def test_getKline(self):
        start = time.perf_counter()
        PERIOD_START = "2021-01-01 00:00:00"
        PERIOD_END = "2021-01-10 23:59:59"
        pair = self.dbService.getPair('BTC', 'USDT')
        candles = self.binance.getHistoricalKlines(pair, Interval.HOUR_1, getDatetime(PERIOD_START),
                                                   getDatetime(PERIOD_END))

        PERIOD_START = "2021-01-03 00:00:00"
        PERIOD_END = "2021-01-13 23:59:59"
        candles = self.binance.getHistoricalKlines(pair, Interval.HOUR_1, getDatetime(PERIOD_START),
                                                   getDatetime(PERIOD_END))
        end = time.perf_counter()
        delta1 = end - start

        start = time.perf_counter()
        PERIOD_START = "2021-01-01 00:00:00"
        candles = self.binance.getHistoricalKlines(pair, Interval.HOUR_1, getDatetime(PERIOD_START),
                                                   getDatetime(PERIOD_END))
        end = time.perf_counter()
        delta2 = end - start
        self.assertLess(delta2, 0.1 * delta1, "Fetching candles from DB should be way faster than from the exchange")

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
        self.assertAlmostEqual(before-after, VOLUME, 5)

        self.assertEqual(self.binance.checkOrder(orderId)['status'], 'FILLED')


if __name__ == '__main__':
    unittest.main()
