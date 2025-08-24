from datetime import datetime, timedelta
from tasks.background import scheduler
import auth.models as models
import auth.strava_helper as strava
import logging

def fetch_strava():
    client = strava.get_strava_client(models.config.strava_access)
    after = datetime.now() - timedelta(minutes=models.config.poll_time_minutes*2)
    activities = client.get_activities(limit=1)
    activity = activities.next()
    if activity is None:
        return
    assert activity.id
    activity = client.get_activity(activity.id)
    assert activity.description
    if models.config.hevy_identification not in activity.description:
        logging.warning("Found strava activity without hevy identification - skipping...")
        return
    
    

def add_job():
    scheduler.add_job(fetch_strava, 'interval', minutes=models.config.poll_time_minutes)
