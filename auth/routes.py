from flask import Blueprint, redirect, url_for, session, request, jsonify
from server import db
from .models import User, StravaAccount
from .oauth import oauth
from . import strava_helper as strava
from auth_utils import *

bp = Blueprint("auth", __name__)


# Google Login
@bp.route("/login/google")
def login_google():
    redirect_uri = url_for("auth.auth_google", _external=True)
    assert oauth.google
    return oauth.google.authorize_redirect(redirect_uri)

@bp.route("/google")
def auth_google():
    assert oauth.google
    token = oauth.google.authorize_access_token()
    userinfo = token["userinfo"]

    email = userinfo["email"]
    google_id = userinfo["sub"]
    user = get_user(email)
    if not user:
        user = User()
        user.email = email
        user.name = userinfo.get("name")
        user.google_id = google_id
        db.session.add(user)
    else:
        user.google_id = google_id
    db.session.commit()

    session["user_id"] = user.id
    return f"Logged in as {user.email}. <a href='/connect/strava'>Connect Strava</a>"

@bp.route("/connect/strava")
def connect_strava():
    return redirect(strava.get_auth_url())


@bp.route("/strava")
def auth_strava():
    if not is_auth():
        return "Not Authorized.", 403
    if not get_user_by_id(session["user_id"]):
        session.clear()
        return "Not Authorized.", 403
    code = request.args.get("code", "")
    client = strava.exchange_token(code)
    account = strava.get_strava_account(session["user_id"])
    athlete = client.get_athlete()
    if not athlete.id:
        return jsonify({"error": "null athlete id"}), 500
    if not account:
        account = StravaAccount()
        account.user_id = session["user_id"]
        account.strava_id = athlete.id
        db.session.add(account)
    strava.validate_tokens(client, account)
    return redirect(url_for("routes.dashboard"))
    
