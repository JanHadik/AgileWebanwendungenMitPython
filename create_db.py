import hashlib
from Flagstravaganza import app, db, models
from instance.flag_list import FLAGS
from config import salt

with app.app_context():
    db.create_all()

    with db.session.begin():
        db.session.query(models.User).delete()
        db.session.query(models.Highscore).delete()
        db.session.query(models.Flag).delete()
    db.session.commit()

    user = models.User("Admin", hashlib.pbkdf2_hmac('sha256', "Adminpassword".encode('utf-8'), salt, 100000))
    db.session.add(user)
    db.session.commit()

    for flag in FLAGS:
        country = models.Flag(flag["image_url"], flag["country"])
        db.session.add(country)
        db.session.commit()
