import datetime
from mailer import Mailer, generate_notes_html
from tasks.background import scheduler
import auth.models as models
import auth.strava_helper as strava
import logging
import hevy_parser as parser

def fetch_strava():
    client = strava.get_strava_client(models.config.strava_access)
    after = datetime.datetime.now(datetime.UTC) - datetime.timedelta(minutes=models.config.poll_time_minutes*2)
    activities = client.get_activities(limit=1, after=after)
    activity = None
    try:
        activity = activities.next()
    except:
        logging.info("No new activities found.")
    if activity is None:
        return
    assert activity.id
    activity = client.get_activity(activity.id)
    assert activity.id
    assert activity.description
    assert activity.name
    if any((report.activity_id == activity.id for report in models.reports.reports)):
        logging.warning("Found existing strava activity - skipping")
        return
    if models.config.hevy_identification not in activity.description:
        logging.warning("Found strava activity without hevy identification - skipping...")
        return
    logging.info("Found new strava activity - sending report")
    name = activity.name
    desc = activity.description
    report = parser.parse_workout(desc, activity_id=activity.id, name=name, previous_reports=models.reports.reports[:models.config.progressive_overload_truncation])
    models.reports.reports.append(report)
    models.reports.save()
    Mailer().send("Fill out report notes - Hevyzer", generate_notes_html(report.activity_id), models.config.emails, html=True)
    
    

def add_job():
    scheduler.add_job(fetch_strava, 'interval', minutes=models.config.poll_time_minutes)
