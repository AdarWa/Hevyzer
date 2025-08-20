from flask import Blueprint, redirect, url_for, session, request, jsonify
from . import strava_helper as strava
from auth.models import config
from os import getenv

bp = Blueprint("auth", __name__)
STRAVA_VERIFY_TOKEN = getenv("STRAVA_VERIFY_TOKEN", "VERIFY_TOKEN")

@bp.route("/connect/strava")
def connect_strava():
    return redirect(strava.get_auth_url())


@bp.route("/strava")
def auth_strava():
    code = request.args.get("code", "")
    client = strava.exchange_token(code)
    access = config.strava_access
    athlete = client.get_athlete()
    if not athlete.id:
        return jsonify({"error": "null athlete id"}), 500
    strava.validate_tokens(client, access)
    return redirect(url_for("routes.dashboard"))
    
@bp.route("/webhook_callback", methods=["GET", "POST"])
def webhook_callback():
    if request.method == "GET":
        return jsonify(strava.get_strava_client(config.strava_access).handle_subscription_callback({k: v[0] for k, v in request.args.items()},STRAVA_VERIFY_TOKEN))
    elif request.method == "POST":
        print(request.form)
        return "OK", 200
    else:
        return "Bad Request", 400
