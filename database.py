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

    first_user = models.User('matthewswain@gmail.com', 'password')
    first_user.activated = True
    session.add(first_user)

    second_user = models.User('matthew.swain@vista.co.nz', 'password')
    second_user.activated = True
    session.add(second_user)

    coke = models.Item('Coke', 45)
    session.add(coke)

    kitkat = models.Item('KitKat', 25)
    session.add(kitkat)

    twix = models.Item('Twix', 40)
    session.add(twix)

    session.commit()
    session.close()