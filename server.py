from datetime import datetime, timedelta
from pathlib import Path
from flask import Flask
import auth.models as models
import auth.strava_helper as strava
import os
from tasks.background import scheduler
import tasks.strava_task as strava_task

app = None

STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID", "")
STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET", "")
STRAVA_REDIRECT_URI = os.getenv("STRAVA_REDIRECT_URI", "")
CONFIG_PATH =str( os.getenv("CONFIG_PATH"))
REPORTS_PATH =str( os.getenv("REPORTS_PATH"))
EXTERNAL_DOMAIN = os.getenv("EXTERNAL_DOMAIN", "")


def run():
    global app
    app = Flask(__name__)
    app.config['SERVER_NAME'] = EXTERNAL_DOMAIN 

    from routes import bp as routes_bp
    from auth.routes import bp as auth_bp
    app.register_blueprint(routes_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")

    app.app_context().push()
    if not Path(CONFIG_PATH).exists():
        models.Config.get_default_config().save(CONFIG_PATH)
    if not Path(REPORTS_PATH).exists():
        models.Reports.get_default_reports().save(REPORTS_PATH)

    models.reports = models.Reports.load(REPORTS_PATH)
    models.config = models.Config.load(CONFIG_PATH)
    strava_task.add_job()
    scheduler.start()
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)
