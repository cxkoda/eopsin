import logging

_log = logging.getLogger(__name__)


class Strategy:
    name: str
    log: logging.Logger

    def __init__(self, name):
        self.name = name
        self.log = _log.getChild(name)
