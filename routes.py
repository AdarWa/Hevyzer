from flask import Blueprint, redirect, render_template, url_for, request
import auth.models as models

bp = Blueprint("routes", __name__)

@bp.route("/")
def index():
    if models.config.strava_access.validate_access():
        return redirect(url_for("routes.dashboard"))
    return render_template("index.html")

@bp.route("/dashboard")
def dashboard():
    if not models.config.strava_access.validate_access():
        return redirect(url_for("routes.index"))
    return render_template("dashboard.html", emails=models.config.emails)

@bp.route("/update_emails", methods=["POST"])
def update_emails():
    emails = request.form.getlist('emails')
    models.config.emails = emails
    models.config.save()
    return redirect(url_for("routes.dashboard"))

@bp.route("/update_settings")
def update_settings():
    return "TODO", 418