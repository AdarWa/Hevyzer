from flask import Blueprint
from auth.auth_utils import is_auth, get_forbidden_msg

bp = Blueprint("routes", __name__)

@bp.route("/")
def index():
    return """
    <a href='auth/login/google'>Login with Google</a><br>
    <a href='auth/connect/strava'>Connect Strava (after Google login)</a><br>
    """

@bp.route("dashboard")
def dashboard():
    if not is_auth():
        return get_forbidden_msg()
    return "TODO"