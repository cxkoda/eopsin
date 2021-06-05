from typing import Callable, List, Dict


class _Event:
    name: str
    targets: List[Callable]

    def __init__(self, name: str):
        self.targets = []
        self.name = name

    def __repr__(self):
        return f'Event<name={self.name}, targets={len(self)}>'

    __str__ = __repr__

    def __call__(self, *args, **kwargs):
        for target in self.targets:
            target(*args, **kwargs)

    def __iadd__(self, target: Callable):
        self.targets.append(target)
        return self

    def __isub__(self, target: Callable):
        while target in self.targets:
            self.targets.remove(target)
        return self

    def __len__(self):
        return len(self.targets)

    def __getitem__(self, item):
        return self.targets[item]


class EventsException(Exception):
    pass


class Events:
    events: List[str]
    _events: Dict[str, _Event]

    def __init__(self, events: List[str] = None, eventClass=_Event):
        if events is not None:
            self.events = events
        self._events = {}

        for name in self.events:
            self._events[name] = eventClass(name)
            self.__dict__[name] = self._events[name]

    def __repr__(self):
        return f'Events<events={self._events}>'

    __str__ = __repr__

    def __assureEventAvailable(self, name: str) -> None:
        if name not in self._events:
            raise EventsException(f'Event not available: {name}')

    def __getattr__(self, name: str) -> _Event:
        self.__assureEventAvailable(name)
        return self._events[name]

    def __getitem__(self, name: str) -> _Event:
        self.__assureEventAvailable(name)
        return self._events[name]

    def __setitem__(self, name: str, value: _Event) -> None:
        self.__assureEventAvailable(name)
        self._events[name] = value

    def __len__(self) -> int:
        return len(self._events)

    def __iter__(self):
        return self._events.values().__iter__()
