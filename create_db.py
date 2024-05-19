import hashlib
from Flagstravaganza import app, db, models
from instance.flag_list import FLAGS
from config import salt

with app.app_context():
    db.create_all()

    user = models.User("Test", hashlib.pbkdf2_hmac('sha256', "Test".encode('utf-8'), salt, 100000))
    db.session.add(user)
    db.session.commit()

    with db.session.begin():
        db.session.query(models.Flag).delete()

    db.session.commit()

    for flag in FLAGS:
        country = models.Flag(flag["image_url"], flag["country"])
        db.session.add(country)
        db.session.commit()
