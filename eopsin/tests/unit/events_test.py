import unittest

import eopsin
from eopsin.util import Events, EventsException


class Callback:
    def __init__(self):
        self.callbackCounter = [0, 0]

    def callback0(self):
        self.callbackCounter[0] += 1

    def callback1(self):
        self.callbackCounter[1] += 1


class TestEvents(unittest.TestCase):
    def setUp(self) -> None:
        self.callback = Callback()

    def test_getattr(self):
        class MyEvents(Events):
            events = ('on_eventOne',)

        with self.assertRaises(EventsException):
            MyEvents().on_eventNotOne += self.callback.callback0

        MyEvents().on_eventOne += self.callback.callback0

    def test_len(self):
        events = Events(events=("on_change", "on_edit"))
        self.assertEqual(2, len(events))

    def test_iter(self):
        events = Events(events=("on_change", "on_get"))
        self.assertEqual(2, len(events))

        i = 0
        for event in events:
            i += 1
            self.assertTrue(isinstance(event, eopsin.util.events._Event))
        self.assertEqual(2, i)

    def test_iterCustomEvent(self):
        class CustomEvent(eopsin.util.events._Event):
            pass

        events = Events(events=("on_change", "on_get", "on_edit"), eventClass=CustomEvent)
        self.assertEqual(3, len(events))

        i = 0
        for event in events:
            i += 1
            self.assertTrue(isinstance(event, CustomEvent))
        self.assertEqual(3, i)


class TestEvent(unittest.TestCase):
    def setUp(self):
        self.callback = Callback()
        self.events = Events(events=("on_change", "on_edit"))
        self.events.on_change += self.callback.callback0
        self.events.on_change += self.callback.callback1
        self.events.on_edit += self.callback.callback1

    def test_type(self):
        ev = self.events.on_change
        self.assertEqual('on_change', ev.name)

    def test_len(self):
        self.assertEqual(2, len(self.events.on_change))
        self.assertEqual(1, len(self.events.on_edit))

    def test_repr(self):
        ev = self.events.on_change
        self.assertEqual("Event<name=on_change, targets=2>", str(ev))

    def test_getitem(self):
        ev = self.events.on_edit
        self.assertEqual(1, len(ev))
        self.assertEqual(ev[0], self.callback.callback1)

        with self.assertRaises(IndexError):
            _ = ev[1]

    def test_isub(self):
        self.events.on_change -= self.callback.callback0
        ev = self.events.on_change
        self.assertEqual(1, len(ev))
        self.assertEqual(ev[0], self.callback.callback1)

    def test_fireEvents(self):
        for event in self.events:
            event()

        self.assertEqual(1, self.callback.callbackCounter[0])
        self.assertEqual(2, self.callback.callbackCounter[1])


if __name__ == '__main__':
    unittest.main()
