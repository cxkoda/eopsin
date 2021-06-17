import datetime
import enum
import typing
from dataclasses import dataclass

from .pair import Pair


@enum.unique
class OrderSide(enum.Enum):
    BUY = 1
    SELL = 2


@enum.unique
class OrderStatus(enum.Enum):
    NEW = 1
    PARTIALLY_FILLED = 2
    FILLED = 3
    CANCELED = 4
    PENDING_CANCEL = 5
    REJECTED = 6
    EXPIRED = 7


@dataclass
class OrderId:
    pair: Pair
    id: int


class Order:
    pair: Pair
    status: OrderStatus


@dataclass
class OrderInfo:
    pair: Pair = None
    orderId: int = None
    time: datetime.datetime = None
    orderedVolume: float = None
    filledVolume: float = None
    filledCurrencyVolume: float = None
    status: OrderStatus = None
    type: str = None
    side: OrderSide = None


@enum.unique
class VolumeType(enum.Enum):
    ASSET = 1
    CURRENCY = 2


class MarketOrder(Order):
    side: OrderSide
    volume: float

    def __init__(self, pair: Pair, side: OrderSide, volume: float, status: OrderStatus = OrderStatus.NEW,
                 volumeType: VolumeType = VolumeType.ASSET):
        self.pair = pair
        self.side = side
        self.volume = volume
        self.status = status
        self.volumeType = volumeType

    @classmethod
    def newSell(cls, pair: Pair, volume: float, volumeType: VolumeType = VolumeType.ASSET):
        return cls(pair, OrderSide.SELL, volume, volumeType=volumeType)

    @classmethod
    def newBuy(cls, pair: Pair, volume: float, volumeType: VolumeType = VolumeType.ASSET):
        return cls(pair, OrderSide.BUY, volume, volumeType=volumeType)

    def __repr__(self):
        return f'<MarketOrder({self.pair}, {self.side}, {self.volume}, {self.volumeType})>'

    __str__ = __repr__


class LimitOrder(Order):
    side: OrderSide
    volume: float
    price: float

    def __init__(self, pair: Pair, side: OrderSide, volume: float, price: float, status: OrderStatus = OrderStatus.NEW):
        self.pair = pair
        self.side = side
        self.volume = volume
        self.price = price
        self.status = status
