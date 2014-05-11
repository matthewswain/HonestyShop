from sqlalchemy import create_engine, Column, Integer, String, ForeignKey 
from sqlalchemy.orm import relationship, backref
from database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    transactions = relationship('Transaction', backref='user')


    def __init__(self, name):
        self.name = name


    def __repr__(self):
        return '<User {0} - {1}>'.format(self.id, self.name)


class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    price = Column(Integer)


    def __init__(self, name, price):
        self.name = name
        self.price = price


    def __repr__(self):
        return '<Item {0} - {1}>'.format(self.id, self.name)


class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    value = Column(Integer)


    def __init__(self, user, item):
        self.user_id = user.id
        self.item_id = item.id
        self.value = item.price


    def __repr__(self):
        return '<Transaction {0}>'.format(self.id)
