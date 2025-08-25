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
    
@bp.route("/logout", methods=["DELETE"])
def logout():
    models.config.strava_access = models.StravaAccess()
    models.config.save()
    return redirect(url_for("routes.index"))

@bp.route("/reset_to_default", methods=["DELETE"])
def reset():
    models.config = models.Config.get_default_config()
    models.reports = models.Reports.get_default_reports()
    models.config.save()
    models.reports.save()
    return redirect(url_for("routes.index"))