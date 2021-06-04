import datetime
import os
import unittest

from sqlalchemy import create_engine

from exchange.binance import BinanceHandler
from exchange.emulator import ExchangeEmulator
from exchange.exchange import MarketOrder, OrderStatus
from model.candle import Interval
from service.dbservice import DBService


class TestBinanceEmulator(unittest.TestCase):

    def __init__(self, *args):
        super().__init__(*args)
        engine = create_engine("sqlite://", echo=False, future=True)
        self.dbService = DBService(engine)
        self.BINANCE_API_KEY = os.environ['BINANCE_TEST_API_KEY']
        self.BINANCE_API_SECRET = os.environ['BINANCE_TEST_API_SECRET']
        self.binance = BinanceHandler(self.dbService, self.BINANCE_API_KEY, self.BINANCE_API_SECRET, testnet=True)

    def setUp(self) -> None:
        self.emulator = ExchangeEmulator(self.binance, portfolio={'BTC': 100})

    def test_basicDelegation(self):
        pair = self.dbService.getPair('BTC', 'USDT')
        interval = Interval.DAY_1
        begin = datetime.datetime(2021, 5, 10, 10, 0, 00)
        end = datetime.datetime(2021, 5, 10, 12, 0, 00)
        self.assertEqual(self.binance._getHistoricalKlinesFromServer(pair, interval, begin, end),
                         self.emulator._getHistoricalKlinesFromServer(pair, interval, begin, end),
                         "_getHistoricalKlinesFromServer should be delegated to the underlying handler")

    def test_portfolio(self):
        self.assertEqual(100, self.emulator.getAssetBalance('BTC'))
        self.assertEqual({'BTC': 100}, self.emulator.getPortfolio())

        self.emulator.getPortfolio()['ETH'] = 100
        self.assertEqual(0, self.emulator.getAssetBalance('ETH'), "Dict changes should not affect the simulator state")

    def test_marketOrder(self):
        pair = self.dbService.getPair('BTC', 'USDT')
        order = MarketOrder.newSell(pair, 30)
        orderId = self.emulator.placeOrder(order)

        self.assertEqual(self.emulator.checkOrder(orderId), OrderStatus.FILLED)
        self.assertEqual(70, self.emulator.getAssetBalance('BTC'))
        self.assertGreater(self.emulator.getAssetBalance('USDT'), 0)


if __name__ == '__main__':
    unittest.main()
