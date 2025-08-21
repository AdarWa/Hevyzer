from datetime import datetime, timedelta
from pathlib import Path
from flask import Flask
import auth.models as models
import auth.strava_helper as strava
from auth.models import config
import os
from tasks.background import scheduler
import tasks.strava_task as strava_task



STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID", "")
STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET", "")
STRAVA_REDIRECT_URI = os.getenv("STRAVA_REDIRECT_URI", "")
CONFIG_PATH =str( os.getenv("CONFIG_PATH"))


def run():
    app = Flask(__name__)
    app.config['SERVER_NAME'] = 'cardinal-amazing-antelope.ngrok-free.app' 

    from routes import bp as routes_bp
    from auth.routes import bp as auth_bp
    app.register_blueprint(routes_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")

    app.app_context().push()
    if not Path(CONFIG_PATH).exists():
        models.Config.get_default_config().save(CONFIG_PATH)

    models.config = models.Config.load(CONFIG_PATH)
    strava_task.add_job()
    scheduler.start()
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)
