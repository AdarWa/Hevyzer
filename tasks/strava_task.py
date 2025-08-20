from apscheduler.schedulers.background import BackgroundScheduler
from auth.models import config
import auth.strava_helper as strava

def fetch_strava():
    client = strava.get_strava_client(config.strava_access)
    client.create_subscription

def add_job(scheduler: BackgroundScheduler):
    scheduler.add_job(fetch_strava, 'interval', minutes=config.poll_time_minutes)
