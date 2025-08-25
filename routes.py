import logging
from flask import Blueprint, redirect, render_template, url_for, request
import auth.models as models
import generator
import tasks.background as bg
import tasks.strava_task as strava_task

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
    return render_template("dashboard.html", emails=models.config.emails, config=models.config, reports=models.reports.reports)

@bp.route("/update_emails", methods=["POST"])
def update_emails():
    emails = request.form.getlist('emails')
    models.config.emails = emails
    models.config.save()
    return redirect(url_for("routes.dashboard"))

@bp.route("/update_settings", methods=["POST"])
def update_settings():
    try:
        models.config.poll_time_minutes = int(request.form["poll_time_minutes"])
        models.config.hevy_identification = request.form["hevy_identification"]
        models.config.progressive_overload_truncation = int(request.form["progressive_overload_truncation"])
        models.config.model = request.form["model"]

        # Update measures
        models.config.measures = models.Measures(
            age=int(request.form["age"]),
            bodyweight=int(request.form["bodyweight"]),
            experience=float(request.form["experience"]),
        )

        models.config.save()

    except Exception as e:
        logging.exception(f"Exception while updating settings: {str(e)}")

    return redirect(url_for("routes.dashboard"))

@bp.route("/report_notes/<int:report_id>", methods=["GET", "POST"])
def report_notes(report_id):
    if request.method == "GET":
        return render_template("report_notes.html")
    elif request.method == "POST":
        report = next((report for report in models.reports.reports if report.activity_id == int(report_id)),None)
        assert report
        report.notes = request.form.get("notes", "")
        models.reports.save()
        bg.scheduler.add_job(generator.send_report, "date", args=(report,))
        return "Report saved successfully."
    else:
        return "Method not allowed", 400
    
@bp.route("/fetch_strava")
def fetch_strava_route():
    limit = request.args.get("limit", 3)
    bg.scheduler.add_job(strava_task.fetch_strava, "date", kwargs={"limit": limit})
    return redirect(url_for("routes.dashboard"))
    
@bp.route("/logout", methods=["POST"])
def logout():
    models.config.strava_access = models.StravaAccess()
    models.config.save()
    return redirect(url_for("routes.index"))

@bp.route("/reset_to_default", methods=["POST"])
def reset():
    models.config = models.Config.get_default_config()
    models.reports = models.Reports.get_default_reports()
    models.config.save()
    models.reports.save()
    return redirect(url_for("routes.index"))