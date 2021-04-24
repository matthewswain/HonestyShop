import models
from app import db


def init_db():

    db.create_all()
    db.session.commit()

    admin_group = models.UserGroup('admin')
    db.session.add(admin_group)
    db.session.commit()

    first_user = models.User('admin@example.com', 'password')
    first_user.activated = True
    db.session.add(first_user)
    db.session.commit()

    admin_membership = models.UserGroupMembership(first_user, admin_group)
    db.session.add(admin_membership)
    db.session.commit()

    second_user = models.User('user@example.com', 'password')
    second_user.activated = True
    db.session.add(second_user)
    db.session.commit()

    third_user = models.User('another_user@example.com', 'password')
    third_user.activated = True
    db.session.add(third_user)
    db.session.commit()

    sprite = models.Item('Sprite', 0.60)
    db.session.add(sprite)
    db.session.commit()

    kitkat = models.Item('KitKat', 0.40)
    db.session.add(kitkat)
    db.session.commit()

    twix = models.Item('Twix', 0.75)
    db.session.add(twix)
    db.session.commit()

    purchase = models.Purchase(second_user, kitkat)
    db.session.add(purchase)
    db.session.commit()

    second_purchase = models.Purchase(second_user, sprite)
    db.session.add(second_purchase)
    db.session.commit()

    third_purchase = models.Purchase(third_user, twix)
    db.session.add(third_purchase)
    db.session.commit()

    db.session.close()
