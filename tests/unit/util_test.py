import unittest
from datetime import datetime, timedelta

from service.util import ceilDatetime, floorDatetime


class TestUtil(unittest.TestCase):

    def test_floorDatetime(self):
        mydate = datetime(2021, 10, 1, 5, 24, 45)
        floored = lambda res: floorDatetime(mydate, res)
        self.assertEqual(datetime(2021, 10, 1, 5, 24, 0), floored(timedelta(minutes=1)))
        self.assertEqual(datetime(2021, 10, 1, 5, 20, 0), floored(timedelta(minutes=5)))
        self.assertEqual(datetime(2021, 10, 1, 5, 0, 0), floored(timedelta(hours=1)))
        self.assertEqual(datetime(2021, 10, 1, 4, 0, 0), floored(timedelta(hours=4)))
        self.assertEqual(datetime(2021, 10, 1, 0, 0, 0), floored(timedelta(days=1)))

    def test_floorDatetimeEqual(self):
        mydate = datetime(2020, 10, 10, 0, 0, 0)
        floored = lambda res: floorDatetime(mydate, res)
        self.assertEqual(mydate, floored(timedelta(minutes=1)))
        self.assertEqual(mydate, floored(timedelta(minutes=5)))
        self.assertEqual(mydate, floored(timedelta(hours=1)))
        self.assertEqual(mydate, floored(timedelta(hours=4)))
        self.assertEqual(mydate, floored(timedelta(days=1)))

    def test_ceilDatetime(self):
        mydate = datetime(2021, 10, 1, 5, 24, 45)
        ceiled = lambda res: ceilDatetime(mydate, res)
        self.assertEqual(datetime(2021, 10, 1, 5, 25, 0), ceiled(timedelta(minutes=1)))
        self.assertEqual(datetime(2021, 10, 1, 5, 25, 0), ceiled(timedelta(minutes=5)))
        self.assertEqual(datetime(2021, 10, 1, 6, 0, 0), ceiled(timedelta(hours=1)))
        self.assertEqual(datetime(2021, 10, 2, 0, 0, 0), ceiled(timedelta(days=1)))

    def test_ceilDatetimeEqual(self):
        mydate = datetime(2020, 10, 10, 0, 0, 0)
        ceiled = lambda res: ceilDatetime(mydate, res)
        self.assertEqual(mydate, ceiled(timedelta(minutes=1)))
        self.assertEqual(mydate, ceiled(timedelta(minutes=5)))
        self.assertEqual(mydate, ceiled(timedelta(hours=1)))
        self.assertEqual(mydate, ceiled(timedelta(hours=4)))
        self.assertEqual(mydate, ceiled(timedelta(days=1)))


if __name__ == '__main__':
    unittest.main()
