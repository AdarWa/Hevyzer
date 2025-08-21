from datetime import datetime, timedelta
from tasks.background import scheduler
import auth.models as models
import auth.strava_helper as strava

def fetch_strava():
    print(models.config.strava_access.model_dump_json())
    client = strava.get_strava_client(models.config.strava_access)
    after = datetime.now() - timedelta(minutes=models.config.poll_time_minutes*2)
    activities = client.get_activities(limit=1)
    activity = activities.next()
    if activity is None:
        return
    print(activity.__dict__)

def add_job():
    scheduler.add_job(fetch_strava, 'interval', minutes=models.config.poll_time_minutes)
