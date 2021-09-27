from app.store.database.gino import db


class SessionModel(db.Model):
    __tablename__ = "sessions"
    id = db.Column(db.Integer(), primary_key=True)
    client = db.Column(db.Integer(), nullable=False, unique=True)
    session = db.Column(db.String())
