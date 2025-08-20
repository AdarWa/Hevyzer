from flask import Blueprint, redirect, render_template, url_for, request
from auth.models import config

bp = Blueprint("routes", __name__)

@bp.route("/")
def index():
    if config.strava_access.validate_access():
        return redirect(url_for("routes.dashboard"))
    return render_template("index.html")

@bp.route("/dashboard")
def dashboard():
    if not config.strava_access.validate_access():
        return redirect(url_for("routes.index"))
    return render_template("dashboard.html", emails=config.emails)

@bp.route("/update_emails", methods=["POST"])
def update_emails():
    emails = request.form.getlist('emails')
    config.emails = emails
    config.save()
    return redirect(url_for("routes.dashboard"))

@bp.route("/update_settings")
def update_settings():
    return "TODO", 418