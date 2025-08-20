from pathlib import Path
from flask import Flask
import auth.models as models
import os

app = Flask(__name__)
app.config['SERVER_NAME'] = 'cardinal-amazing-antelope.ngrok-free.app' 


STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID", "")
STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET", "")
STRAVA_REDIRECT_URI = os.getenv("STRAVA_REDIRECT_URI", "")
CONFIG_PATH =str( os.getenv("CONFIG_PATH"))

if not Path(CONFIG_PATH).exists():
    models.Config.get_default_config().save(CONFIG_PATH)

models.config = models.Config.load(CONFIG_PATH)

from routes import bp as routes_bp
from auth.routes import bp as auth_bp
app.register_blueprint(routes_bp)
app.register_blueprint(auth_bp, url_prefix="/auth")

def run():
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)
