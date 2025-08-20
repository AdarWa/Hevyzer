from flask import Blueprint, redirect, url_for, session, request, jsonify
from . import strava_helper as strava
from auth.models import config

bp = Blueprint("auth", __name__)

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
    
