from flask_sqlalchemy import SQLAlchemy
from security import Authentication
from datetime import datetime


db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    salt = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    name = db.Column(db.String)
    activated = db.Column(db.Boolean, nullable=False)
    purchases = db.relationship('Purchase', backref='user')
    payments = db.relationship('Payment', backref='user')
    password_tokens = db.relationship('PasswordToken', backref='user')
    activation_tokens = db.relationship('ActivationToken', backref='user')
    memberships = db.relationship('UserGroupMembership', backref='user')
    pin = db.Column(db.String)

    def set_password(self, password):
        self.salt = Authentication.random_string(10)
        self.password = Authentication.salt_and_hash(password.encode('utf-8'), self.salt.encode('utf-8'))

    def set_pin(self, pin):
        self.pin = Authentication.salt_and_hash(pin.encode('utf-8'), self.salt.encode('utf-8'))

    def get_group_names(self):
        group_names = []

        for membership in self.memberships:
            group_names.append(membership.group.name)

        return group_names

    def is_member(self, group_name):

        group_names = self.get_group_names()

        if group_name in group_names:
            return True
        else:
            return False

    def __init__(self, email, password):
        self.email = email.lower()
        self.set_password(password)
        self.activated = False

    def __repr__(self):
        return '<User {0} - {1}>'.format(self.id, self.email)

    @staticmethod
    def get(email):
        return User.query.filter(User.email == email.lower()).first()


class PasswordToken(db.Model):
    __tablename__ = 'password_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    url_part = db.Column(db.String, nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    hashed_password = db.Column(db.String)
    timestamp = db.Column(db.DateTime, nullable=False)
    
    def __init__(self, user, password):
        self.url_part = Authentication.random_string(30)
        self.user_id = user.id
        self.hashed_password = Authentication.salt_and_hash(password.encode('utf-8'), user.salt.encode('utf-8'))
        self.timestamp = datetime.now()
    

class ActivationToken(db.Model):
    __tablename__ = 'activation_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    url_part = db.Column(db.String, nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    
    def __init__(self, user):
        self.url_part = Authentication.random_string(30)
        self.user_id = user.id
        self.timestamp = datetime.now()
    

class UserGroup(db.Model):
    __tablename__ = 'user_groups'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    memberships = db.relationship('UserGroupMembership', backref="group")

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<UserGroup {0} - {1}>'.format(self.id, self.name)


class UserGroupMembership(db.Model):
    __tablename__ = 'users_to_user_groups'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('user_groups.id'), nullable=False)
    
    def __init__(self, user, user_group):
        self.user_id = user.id
        self.group_id = user_group.id

    def __repr__(self):
        return '<UserGroupMembership {0} - {1}>'.format(self.user.email, self.group.name)


class Item(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    price = db.Column(db.Numeric(6, 2))
    active = db.Column(db.Boolean, nullable=False, default=True)
    purchases = db.relationship('Purchase', backref='item')
    
    def __init__(self, name, price):
        self.name = name
        self.price = price

    def __repr__(self):
        return '<Item {0} - {1}>'.format(self.id, self.name)


class Purchase(db.Model):
    __tablename__ = 'Purchases'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    price = db.Column(db.Numeric(6, 2), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)

    def __init__(self, user, item):
        self.user_id = user.id
        self.item_id = item.id
        self.price = item.price
        self.timestamp = datetime.now()

    def __repr__(self):
        return '<Purchase {0}>'.format(self.id)
        
    
class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    value = db.Column(db.Numeric(6, 2), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)

    def __init__(self, user, value):
        self.user_id = user.id
        self.value = value
        self.timestamp = datetime.now()

    def __repr__(self):        
        return '<Payment {0}>'.format(self.id)
