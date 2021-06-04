import enum

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


class OrderId:
    pair: Pair
    id: int

    def __init__(self, pair: Pair, id: int):
        self.pair = pair
        self.id = id

    def __repr__(self):
        return f'<OrderId(pair={self.pair}, id={self.id}>'


class Order:
    pair: Pair
    status: OrderStatus


class MarketOrder(Order):
    side: OrderSide
    volume: float

    def __init__(self, pair: Pair, side: OrderSide, volume: float, status: OrderStatus = OrderStatus.NEW):
        self.pair = pair
        self.side = side
        self.volume = volume
        self.status = status

    @classmethod
    def newSell(cls, pair: Pair, volume: float):
        return cls(pair, OrderSide.SELL, volume)

    @classmethod
    def newBuy(cls, pair: Pair, volume: float):
        return cls(pair, OrderSide.BUY, volume)


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
