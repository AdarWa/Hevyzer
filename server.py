from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
from auth import oauth


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID", "")
STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET", "")
STRAVA_REDIRECT_URI = os.getenv("STRAVA_REDIRECT_URI", "")

app.app_context().push()

db = SQLAlchemy()
db.init_app(app)

import auth.models
db.create_all()


oauth.init_oauth(app)
from routes import bp as routes_bp
from auth.routes import bp as auth_bp
app.register_blueprint(routes_bp)
app.register_blueprint(auth_bp, url_prefix="/auth")

def run():
    app.run(host="0.0.0.0", port=5000, debug=True)
