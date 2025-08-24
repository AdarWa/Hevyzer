from typing import cast
from flask import Blueprint, redirect, url_for, request, jsonify
from . import strava_helper as strava
import auth.models as models
from stravalib.exc import Fault
from os import getenv
from tasks.background import scheduler
from tasks.strava_task import fetch_strava

bp = Blueprint("auth", __name__)
STRAVA_VERIFY_TOKEN = getenv("STRAVA_VERIFY_TOKEN", "VERIFY_TOKEN")

@bp.route("/connect/strava")
def connect_strava():
    return redirect(strava.get_auth_url())


@bp.route("/strava")
def auth_strava():
    code = request.args.get("code", "")
    client = strava.exchange_token(code)
    access = models.config.strava_access
    athlete = client.get_athlete()
    if not athlete.id:
        return jsonify({"error": "null athlete id"}), 500
    access.strava_id = athlete.id
    try:
        strava.create_subscription(client)
    except Fault as e:
        if "already exists" not in str(e):
            print(str(e))
            return "Internal Server Error", 500
    strava.validate_tokens(client, access)
    models.config.save()
    return redirect(url_for("routes.dashboard"))
    
# TODO: Add rate limiting
@bp.route("/webhook_callback", methods=["GET", "POST"])
def webhook_callback():
    if request.method == "GET":
        flattend = {k: v for k, v in request.args.items()}
        response = None
        try:
            response = jsonify(strava.get_strava_client(models.config.strava_access).handle_subscription_callback(flattend,STRAVA_VERIFY_TOKEN))
        except Exception as e:
            return "Already exists."
        return response
    elif request.method == "POST":
        hook = cast(dict,request.json)
        if hook.get("aspect_type", "") == "create":
            if hook.get("owner_id", -1) == models.config.strava_access.strava_id:
                scheduler.add_job(fetch_strava, "date")
        return "OK", 200
    else:
        return "Bad Request", 400