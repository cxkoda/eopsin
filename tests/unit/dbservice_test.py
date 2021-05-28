import datetime
import unittest

from sqlalchemy import create_engine
from service.dbservice import DBService
from model.candle import Candle, Interval
from sqlalchemy.exc import IntegrityError

getDatetime = lambda date: datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')


class TestDBService(unittest.TestCase):

    def setUp(self) -> None:
        engine = create_engine("sqlite://", echo=False, future=True)
        self.dbService = DBService(engine)

    def test_exchange(self):
        self.assertEqual(self.dbService.findExchange('Binance'), None, "DB should be empty")
        binance = self.dbService.addExchange('Binance')
        self.assertEqual(self.dbService.findExchange('Binance'), binance, "Binance should be in db")
        self.assertEqual(binance.id, 1)
        self.assertEqual(binance.name, 'Binance')
        self.assertEqual(self.dbService.getExchange('Binance'), binance, "Binance should be in db")

    def test_missingCandles(self):
        binance = self.dbService.addExchange('Binance')
        pair = self.dbService.getPair('BTC', 'USDT')
        self.dbService.addCandle(
            Candle(exchange=binance, pair=pair, interval=Interval.DAY_1, openTime=getDatetime('2021-01-03 00:00:00')))
        self.dbService.addCandle(
            Candle(exchange=binance, pair=pair, interval=Interval.DAY_1, openTime=getDatetime('2021-01-06 00:00:00')))
        missingPeriods = self.dbService.findMissingCandlePeriods(binance, pair, Interval.DAY_1,
                                                                 getDatetime('2021-01-01 00:00:00'),
                                                                 getDatetime('2021-01-10 00:00:00'))
        self.assertEqual(missingPeriods[0], [getDatetime('2021-01-01 00:00:00'), getDatetime('2021-01-03 00:00:00')])
        self.assertEqual(missingPeriods[1], [getDatetime('2021-01-04 00:00:00'), getDatetime('2021-01-06 00:00:00')])
        self.assertEqual(missingPeriods[2], [getDatetime('2021-01-07 00:00:00'), getDatetime('2021-01-10 00:00:00')])

    def test_sameExchange(self):
        ''' Tests the behaviour for a second identical exchange entity '''

        binance1 = self.dbService.addExchange('Binance')
        with self.assertRaises(IntegrityError):
            self.dbService.addExchange('Binance')


if __name__ == '__main__':
    unittest.main()
