from sqlalchemy import create_engine, Column, Integer, String, ForeignKey 
from sqlalchemy.orm import relationship, backref
from database import Base
from random import choice
from string import ascii_uppercase, ascii_lowercase, digits
from hashlib import sha512

class Security:


    @staticmethod
    def make_salt():

        salt = ''

        for i in range(0, 10):
            salt += choice(ascii_uppercase + ascii_lowercase + digits)

        return salt


    @staticmethod
    def salt_and_hash(password, salt):
        return sha512(password + salt).hexdigest()

    @staticmethod
    def authenticate(user, password):

        if user.password == Security.salt_and_hash(password, user.salt):
            return True
        else:
            return False


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    salt = Column(String, nullable=False)
    password = Column(String, nullable=False)
    name = Column(String)
    transactions = relationship('Transaction', backref='user')
    

    def __init__(self, email, password):
        self.email = email
        self.salt = Security.make_salt()
        self.password = Security.salt_and_hash(password, self.salt)


    def __repr__(self):
        return '<User {0} - {1}>'.format(self.id, self.email)


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
