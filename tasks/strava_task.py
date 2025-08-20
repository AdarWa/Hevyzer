from apscheduler.schedulers.background import BackgroundScheduler
from auth.models import config

def fetch_strava():
    pass

def add_job(scheduler: BackgroundScheduler):
    scheduler.add_job(fetch_strava, 'interval', minutes=config.poll_time_minutes)
