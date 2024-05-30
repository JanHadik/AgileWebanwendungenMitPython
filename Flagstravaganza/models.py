from Flagstravaganza import db


class User(db.Model):
    id: db.Mapped[int] = db.mapped_column(primary_key=True)
    username: db.Mapped[str]
    password: db.Mapped[str]

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return f"User ID: {self.id}, Username: {self.username}"


class Highscore(db.Model):
    id: db.Mapped[int] = db.mapped_column(primary_key=True)
    user: db.Mapped[str] = db.mapped_column(db.ForeignKey(User.id))
    score: db.Mapped[int]

    def __init__(self, user, score):
        self.user = user
        self.score = score

    def __repr__(self):
        return f"Highscore ID: {self.id}, Username: {self.user}, Score: {self.score}"


class Flag(db.Model):
    id: db.Mapped[int] = db.mapped_column(primary_key=True)
    img_path: db.Mapped[str]
    country: db.Mapped[str]

    def __init__(self, img_path, country):
        self.img_path = img_path
        self.country = country

    def __repr__(self):
        return f"Flag ID: {self.id}, Country: {self.country}"
