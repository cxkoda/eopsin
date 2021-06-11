import datetime
import unittest

import sqlalchemy as sql

import eopsin as eop

getDatetime = lambda date: datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S').replace(tzinfo=datetime.timezone.utc)


class TestDBService(unittest.TestCase):

    def setUp(self) -> None:
        engine = sql.create_engine("sqlite://", echo=False, future=True)
        self.dbService = eop.DBService(engine)

    def test_exchange(self):
        self.assertEqual(self.dbService.findExchange('Binance'), None, "DB should be empty")
        binance = self.dbService.addExchange('Binance')
        self.assertEqual(self.dbService.findExchange('Binance'), binance, "Binance should be in db")
        self.assertEqual(binance.id, 1)
        self.assertEqual(binance.name, 'Binance')
        self.assertEqual(self.dbService.getExchange('Binance'), binance, "Binance should be in db")

    def test_addGetSingleCandle(self):
        binance = self.dbService.addExchange('Binance')
        pair = self.dbService.getPair('BTC', 'USDT')
        interval = eop.Interval.MINUTE_1
        openTime1 = datetime.datetime(2021, 2, 10, 10, 55, 00, tzinfo=datetime.timezone.utc)
        openTime2 = datetime.datetime(2021, 2, 10, 10, 56, 00, tzinfo=datetime.timezone.utc)
        self.dbService.addCandle(
            eop.Candle(exchange=binance, pair=pair, interval=interval, openTime=openTime1, closeTime=openTime2))

        candles = self.dbService.findCandles(binance, pair, interval, openTime1, openTime2)
        self.assertEqual(1, len(candles), "Should only find one candle")
        self.assertEqual(openTime1, candles[0].openTime, "Wrong candle found")

        closeTime = datetime.datetime(2021, 2, 10, 10, 57, 00, tzinfo=datetime.timezone.utc)
        self.dbService.addCandle(
            eop.Candle(exchange=binance, pair=pair, interval=interval, openTime=openTime2, closeTime=closeTime))

        candles = self.dbService.findCandles(binance, pair, interval, openTime1, openTime2)
        self.assertEqual(1, len(candles), "Should only find one candle")
        self.assertEqual(openTime1, candles[0].openTime, "Wrong candle found")

        candles = self.dbService.findCandles(binance, pair, interval, openTime2, closeTime)
        self.assertEqual(1, len(candles), "Should only find one candle")
        self.assertEqual(openTime2, candles[0].openTime, "Wrong candle found")

    def test_missingCandles(self):
        binance = self.dbService.addExchange('Binance')
        pair = self.dbService.getPair('BTC', 'USDT')
        self.dbService.addCandle(
            eop.Candle(exchange=binance, pair=pair, interval=eop.Interval.DAY_1,
                       openTime=getDatetime('2021-01-03 00:00:00'),
                       closeTime=getDatetime('2021-01-04 00:00:00')))
        self.dbService.addCandle(
            eop.Candle(exchange=binance, pair=pair, interval=eop.Interval.DAY_1,
                       openTime=getDatetime('2021-01-06 00:00:00'),
                       closeTime=getDatetime('2021-01-07 00:00:00')))
        missingPeriods = self.dbService.findMissingCandlePeriods(binance, pair, eop.Interval.DAY_1,
                                                                 getDatetime('2021-01-01 00:00:00'),
                                                                 getDatetime('2021-01-10 00:00:00'))
        self.assertEqual([getDatetime('2021-01-01 00:00:00'), getDatetime('2021-01-03 00:00:00')], missingPeriods[0])
        self.assertEqual([getDatetime('2021-01-04 00:00:00'), getDatetime('2021-01-06 00:00:00')], missingPeriods[1])
        self.assertEqual([getDatetime('2021-01-07 00:00:00'), getDatetime('2021-01-10 00:00:00')], missingPeriods[2])

    def test_singleMissingCandle(self):
        binance = self.dbService.addExchange('Binance')
        pair = self.dbService.getPair('BTC', 'USDT')
        interval = eop.Interval.MINUTE_1
        openTime = datetime.datetime(2021, 2, 10, 10, 55, 00, tzinfo=datetime.timezone.utc)
        closeTime = datetime.datetime(2021, 2, 10, 10, 56, 00, tzinfo=datetime.timezone.utc)

        missingPeriods = self.dbService.findMissingCandlePeriods(binance, pair, eop.Interval.MINUTE_1, openTime,
                                                                 closeTime)

        self.assertEqual(1, len(missingPeriods), "Only one candle should be identified")
        self.assertEqual([openTime, closeTime], missingPeriods[0], "Begin and end should match the rounded datetimes")

        # Add missing candle and test again
        self.dbService.addCandle(
            eop.Candle(exchange=binance, pair=pair, interval=interval, openTime=openTime, closeTime=closeTime))
        missingPeriods = self.dbService.findMissingCandlePeriods(binance, pair, eop.Interval.MINUTE_1, openTime,
                                                                 closeTime)
        self.assertEqual([], missingPeriods, "the candle should no longer be missing after added.")

    def test_sameExchange(self):
        ''' Tests the behaviour for a second identical exchange entity '''

        binance1 = self.dbService.addExchange('Binance')
        with self.assertRaises(sql.exc.IntegrityError):
            self.dbService.addExchange('Binance')

    def test_CandleTimezone(self):
        binance = self.dbService.addExchange('Binance')
        pair = self.dbService.getPair('BTC', 'USDT')
        interval = eop.Interval.MINUTE_1
        openTime = datetime.datetime(2021, 2, 10, 10, 55, 00)
        closeTime = datetime.datetime(2021, 2, 10, 10, 56, 00)
        self.dbService.addCandle(
            eop.Candle(exchange=binance, pair=pair, interval=interval, openTime=openTime, closeTime=closeTime))
        candles = self.dbService.findCandles(binance, pair, interval, openTime, closeTime)

        self.assertEqual(openTime.astimezone(datetime.timezone.utc), candles[0].openTime)
        self.assertEqual(closeTime.astimezone(datetime.timezone.utc), candles[0].closeTime)


if __name__ == '__main__':
    unittest.main()
