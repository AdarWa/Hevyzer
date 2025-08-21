from datetime import datetime, timedelta
from tasks.background import scheduler
from auth.models import config,load_config
import auth.strava_helper as strava

def fetch_strava():
    load_config()
    print(config.strava_access.model_dump_json())
    client = strava.get_strava_client(config.strava_access)
    after = datetime.now() - timedelta(minutes=config.poll_time_minutes*2)
    activities = client.get_activities(limit=1)
    activity = activities.next()
    if activity is None:
        return
    print(activity.__dict__)

def add_job():
    print(config.model_dump_json())
    scheduler.add_job(fetch_strava, 'interval', minutes=config.poll_time_minutes)
