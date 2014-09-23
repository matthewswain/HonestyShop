import models
from app import db


def init_db():

    db.create_all()
    db.session.commit()

    admin_group = models.UserGroup('admin')
    db.session.add(admin_group)
    db.session.commit()

    first_user = models.User('matthewswain@gmail.com', 'password')
    first_user.activated = True
    db.session.add(first_user)
    db.session.commit()

    admin_membership = models.UserGroupMembership(first_user, admin_group)
    db.session.add(admin_membership)
    db.session.commit()

    second_user = models.User('matthew.swain@vista.co', 'password')
    second_user.activated = True
    db.session.add(second_user)
    db.session.commit()

    coke = models.Item('Coke', 0.45)
    db.session.add(coke)
    db.session.commit()

    kitkat = models.Item('KitKat', 0.25)
    db.session.add(kitkat)
    db.session.commit()

    twix = models.Item('Twix', 0.40)
    db.session.add(twix)
    db.session.commit()

    db.session.close()