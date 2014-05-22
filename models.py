from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship, backref
from database import Base
from security import Authentication
from datetime import datetime

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    salt = Column(String, nullable=False)
    password = Column(String, nullable=False)
    name = Column(String)
    activated = Column(Boolean, nullable=False)
    purchases = relationship('Purchase', backref='user')
    payments = relationship('Payment', backref='user')


    def set_password(self, password):
        self.salt = Authentication.random_string(10)
        self.password = Authentication.salt_and_hash(password, self.salt)


    def __init__(self, email, password):
        self.email = email
        self.set_password(password)
        self.activated = False


    def __repr__(self):
        return '<User {0} - {1}>'.format(self.id, self.email)

    
    @staticmethod
    def get(email):
        return User.query.filter(User.email==email).first()

        
class PasswordToken(Base):
    __tablename__ = 'password_tokens'
    
    id = Column(Integer, primary_key=True)
    url_part = Column(String, nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    
    def __init__(self, user):
        self.url_part = Authentication.random_string(30)
        self.user_id = user.id
        self.timestamp = datetime.now()
    

class UserGroup(Base):
    __tablename__ = 'user_groups'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    

class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    price = Column(Integer)
    Purchases = relationship('Purchase', backref='item')

    
    def __init__(self, name, price):
        self.name = name
        self.price = price


    def __repr__(self):
        return '<Item {0} - {1}>'.format(self.id, self.name)


class Purchase(Base):
    __tablename__ = 'Purchases'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)
    price = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False)


    def __init__(self, user, item):
        self.user_id = user.id
        self.item_id = item.id
        self.price = item.price
        self.timestamp = datetime.now()


    def __repr__(self):
        return '<Purchase {0}>'.format(self.id)
        
    
class Payment(Base):
    __tablename__ = 'payments'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    value = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False)


    def __init__(self, user, value):
        self.user_id = user.id
        self.value = value
        self.timestamp = datetime.now()


    def __repr__(self):        
        return '<Payment {0}>'.format(self.id)

