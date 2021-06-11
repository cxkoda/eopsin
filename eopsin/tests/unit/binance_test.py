import datetime
import os
import unittest

import numpy as np
import sqlalchemy as sql
import timeout_decorator

import eopsin as eop


class TestBinanceBasic(unittest.TestCase):

    def setUp(self) -> None:
        engine = sql.create_engine("sqlite://", echo=False, future=True)
        self.dbService = eop.DBService(engine)
        self.BINANCE_API_KEY = os.environ['BINANCE_TEST_API_KEY']
        self.BINANCE_API_SECRET = os.environ['BINANCE_TEST_API_SECRET']
        self.binance = eop.BinanceHandler(self.dbService, self.BINANCE_API_KEY, self.BINANCE_API_SECRET, testnet=True)

    def test_connection(self):
        self.binance.client.ping()

    def test_portfolio(self):
        portfolio = self.binance.getPortfolio()
        self.assertEqual(portfolio['ETH'], self.binance.getAssetBalance('ETH'))

    def test_marketOrder(self):
        VOLUME = 1e-3

        before = self.binance.getAssetBalance('BTC')
        pair = self.dbService.getPair('BTC', 'USDT')
        order = eop.MarketOrder(pair, eop.OrderSide.SELL, VOLUME)
        orderId = self.binance.placeOrder(order)
        after = self.binance.getAssetBalance('BTC')
        # This causes a problem in the CI, where multiple orders are made simultaneously.
        # self.assertAlmostEqual(VOLUME, before - after, 4)

        self.assertEqual(self.binance.checkOrder(orderId), eop.OrderStatus.FILLED)

    def test_serverTime(self):
        serverTime = self.binance.getTime()
        now = datetime.datetime.now().astimezone(datetime.timezone.utc)
        self.assertLess(np.abs((serverTime - now).total_seconds()), 1)

    @timeout_decorator.timeout(70)
    def test_minuteTrigger(self):
        class TriggerMinuteOnce:
            def __init__(self):
                self.eventCount = 0
                self.loopCount = 0

            def eventCallback(self):
                self.eventCount += 1

            def terminateCallback(self):
                terminate = (self.eventCount > 0)
                if not terminate:
                    self.loopCount += 1

                return terminate

        handler = TriggerMinuteOnce()

        # Test all 3 possible ways to add functions
        self.binance.events.onNewCandle_MINUTE_1 += handler.eventCallback
        self.binance.events['onNewCandle_MINUTE_1'] += handler.eventCallback
        self.binance.events[eop.Interval.MINUTE_1] += handler.eventCallback

        self.binance.eventLoop(datetime.timedelta(seconds=10), terminate=handler.terminateCallback)

        self.assertEqual(3, handler.eventCount)
        self.assertLess(handler.loopCount, 7)


def utcdate(*args):
    return datetime.datetime(*args, tzinfo=datetime.timezone.utc)


class TestBinanceKlines(unittest.TestCase):

    def setUp(self) -> None:
        engine = sql.create_engine("sqlite://", echo=False, future=True)
        self.dbService = eop.DBService(engine)
        self.BINANCE_API_KEY = os.environ['BINANCE_TEST_API_KEY']
        self.BINANCE_API_SECRET = os.environ['BINANCE_TEST_API_SECRET']

        # API issue: Klines are not available on the testnet -> switching to normal server
        self.binance = eop.BinanceHandler(self.dbService, self.BINANCE_API_KEY, self.BINANCE_API_SECRET)

    def test_getKlines(self):
        PERIOD_START = utcdate(2021, 1, 2, 0, 0, 0) - datetime.timedelta(seconds=10)
        PERIOD_END = utcdate(2021, 1, 11, 0, 0, 0)
        pair = self.dbService.getPair('BTC', 'USDT')
        candles = self.binance.getHistoricalKlines(pair, eop.Interval.HOUR_1, PERIOD_START, PERIOD_END)
        self.assertEqual(216, len(candles))

        PERIOD_START = utcdate(2021, 1, 3, 0, 0, 0)
        PERIOD_END = utcdate(2021, 1, 14, 0, 0, 0)
        candles = self.binance.getHistoricalKlines(pair, eop.Interval.HOUR_1, PERIOD_START, PERIOD_END)
        self.assertEqual(264, len(candles))

        PERIOD_START = utcdate(2021, 1, 2, 0, 0, 0)
        candles = self.binance.getHistoricalKlines(pair, eop.Interval.HOUR_1, PERIOD_START, PERIOD_END)
        self.assertEqual(288, len(candles))

    def test_getSingleKlineFromServer(self):
        pair = self.dbService.getPair('BTC', 'USDT')
        interval = eop.Interval.MINUTE_1
        openTime = utcdate(2021, 5, 10, 10, 55, 00)
        closeTime = utcdate(2021, 5, 10, 10, 56, 00)
        candles = self.binance.getHistoricalKlines(pair, interval, openTime, closeTime)
        self.assertEqual(1, len(candles))
        self.assertEqual(openTime, candles[0].openTime)

    def test_lastCompleteCandle(self):
        pair = self.dbService.getPair('BTC', 'USDT')
        interval = eop.Interval.MINUTE_1
        now = utcdate(2021, 2, 10, 10, 56, 11)
        candle = self.binance.getLastCompleteCandleBefore(pair, interval, now)

        begin = utcdate(2021, 2, 10, 10, 55, 00)
        self.assertEqual(begin, candle.openTime)


if __name__ == '__main__':
    unittest.main()
