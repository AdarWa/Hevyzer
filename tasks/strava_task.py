import datetime
from mailer import Mailer, generate_notes_html
from tasks.background import scheduler
import auth.models as models
import auth.strava_helper as strava
import logging
import hevy_parser as parser
from stravalib.model import SummaryActivity
from stravalib.client import Client

def fetch_strava(limit=3):
    logging.info("Fetching Strava for new activities...")
    client = strava.get_strava_client(models.config.strava_access)
    # after = datetime.datetime.now(datetime.UTC) - datetime.timedelta(minutes=models.config.poll_time_minutes*2)
    activities = client.get_activities(limit=limit)
    strava.validate_tokens(client, models.config.strava_access)
    activities_left = True
    while activities_left:
        try:
            activity = activities.next()
            process_activity(activity, client)
        except:
            activities_left = False

def process_activity(activity: SummaryActivity, client: Client):
    if activity is None:
        return
    if any((report.activity_id == activity.id for report in models.reports.reports)):
        logging.warning("Found existing strava activity - skipping")
        return
    assert activity.id
    activity = client.get_activity(activity.id)
    assert activity.id
    if activity.description is None:
        logging.warning("Found Strava activity without description - skipping...")
        return
    assert activity.name
    if models.config.hevy_identification not in activity.description:
        logging.warning("Found strava activity without hevy identification - skipping...")
        return
    logging.info("Found new strava activity - sending report")
    name = activity.name
    desc = activity.description
    report = parser.parse_workout(desc, activity_id=activity.id, name=name, previous_reports=models.reports.reports[:models.config.progressive_overload_truncation])
    models.reports.reports.append(report)
    models.reports.save()
    Mailer().send(f"Fill out report notes - {report.name}", generate_notes_html(report.activity_id), models.config.emails, html=True)
    
    

def add_job():
    scheduler.add_job(fetch_strava, 'interval', minutes=models.config.poll_time_minutes)
