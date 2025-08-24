import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional

from flask import render_template, url_for

import server


class Mailer:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "localhost")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_from = os.getenv("SMTP_FROM")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.use_tls = os.getenv("SMTP_USE_TLS", "true").lower() in ["true", "1", "yes"]

    def send(
        self,
        subject: str,
        body: str,
        to: List[str],
        from_addr: Optional[str] = None,
        html: bool = False
    ):
        if not from_addr:
            from_addr = self.smtp_from

        assert from_addr
        # Build message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = from_addr
        msg["To"] = ", ".join(to)

        if html:
            msg.attach(MIMEText(body, "html"))
        else:
            msg.attach(MIMEText(body, "plain"))

        # Send email
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            if self.use_tls:
                server.starttls()
            if self.smtp_user and self.smtp_password:
                server.login(self.smtp_user, self.smtp_password)
            server.sendmail(from_addr, to, msg.as_string())


def generate_notes_html(report_id: int) -> str:
    """
    Renders the workout email HTML from the template file
    """
    with server.app.app_context():
        return render_template(
            "workout_email.html",
            report_link=url_for("routes.report_notes", report_id=report_id, _external=True, _scheme="https")
        )