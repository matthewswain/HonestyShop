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

    admin_group = models.UserGroup('admin')
    session.add(admin_group)
    session.commit()

    first_user = models.User('matthewswain@gmail.com', 'password')
    first_user.activated = True
    session.add(first_user)
    session.commit()

    admin_membership = models.UserGroupMembership(first_user, admin_group)
    session.add(admin_membership)
    session.commit()

    second_user = models.User('matthew.swain@vista.co.nz', 'password')
    second_user.activated = True
    session.add(second_user)
    session.commit()

    coke = models.Item('Coke', 45)
    session.add(coke)
    session.commit()

    kitkat = models.Item('KitKat', 25)
    session.add(kitkat)
    session.commit()

    twix = models.Item('Twix', 40)
    session.add(twix)
    session.commit()

    session.close()