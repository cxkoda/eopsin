from model.exchange import Exchange
from model.pair import Pair

from sqlalchemy import and_


class DBService:
    def __init__(self, session):
        self.session = session

    def getExchange(self, name: str):
        exchange = self.session.query(Exchange).filter(Exchange.name == name).first()
        if exchange is None:
            exchange = Exchange(name=name)
            self.session.add(exchange)
        return exchange

    def getPair(self, asset: str, currency: str, exchangeName: str):
        exchange = self.getExchange(exchangeName)
        pair = self.session.query(Pair).filter(and_(
            Pair.asset == asset, Pair.currency == currency, Pair.exchange_id == exchange.id)).first()
        if pair is None:
            pair = Pair(asset=asset, currency=currency, exchange=exchange)
            self.session.add(pair)
        return pair
