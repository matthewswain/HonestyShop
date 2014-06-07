from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///honesty.db')
session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = session.query_property()

def init_db():
    import models
    Base.metadata.create_all(engine)

    user = models.User('matthewswain@gmail.com', 'password')
    session.add(user)

    coke = models.Item('Coke', 45)
    session.add(coke)

    chocolate = models.Item('Chocolate', 40)
    session.add(chocolate)

    session.commit()
    session.close()