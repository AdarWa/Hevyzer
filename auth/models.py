from server import db
from sqlalchemy.dialects.postgresql import BIGINT

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255))
    google_id = db.Column(db.String(255), unique=True)

    strava = db.relationship("StravaAccount", back_populates="user", uselist=False)

class StravaAccount(db.Model):
    __tablename__ = "user_strava"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    strava_id = db.Column(BIGINT, unique=True, nullable=False)
    access_token = db.Column(db.Text, nullable=False)
    refresh_token = db.Column(db.Text, nullable=False)
    expires_at = db.Column(BIGINT, nullable=False)

    user = db.relationship("User", back_populates="strava")
