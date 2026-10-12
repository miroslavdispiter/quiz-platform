import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

class EmailSender:
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.email_user = os.getenv("EMAIL_USER")
        self.email_pass = os.getenv("EMAIL_PASS")
        self.email_from = os.getenv("EMAIL_FROM", self.email_user)

    def send_role_change_email(self, to_email: str, new_role: str, full_name: str):
        
        """
        Sends a notification to the user that his role has been changed.
        """

        subject = "Role change on the platform"
        body = (
            f"Dear {full_name},<br><br>"
            f"The administrator has just changed your role on the platform. "
            f"New role: <b>{new_role}</b>.<br><br>"
            f"You now have access to the features that match that role.<br>"
            f"<br>Best regards,<br>Quiz Platform Team"
        )

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self.email_from
        msg["To"] = to_email

        msg.attach(MIMEText(body, "html"))

        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            server.login(self.email_user, self.email_pass)
            server.send_message(msg)

    def send_quiz_result_email(self, to_email, quiz_title, score, total, percentage):
        subject= f"Quiz result: {quiz_title}"
        status = "PASSED!" if percentage >= 60 else "FAILED."

        body = (
            f"<h3>Your quiz results {quiz_title}</h3>"
            f"<p>Points: <b>{score} / {total}</b></p>"
            f"<p>Percentage: <b>{percentage}%</b></p>"
            f"<p>Status: <b>{status}</b></p>"
        )

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self.email_from
        msg["To"] = to_email
        msg.attach(MIMEText(body, "html"))

        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_pass)
                server.send_message(msg)
        except Exception as e:
            print(f"Error sending mail: {e}")
            

    def send_pdf_report(self, to_email: str, subject: str, body_html: str, pdf_bytes: bytes, filename: str = "report.pdf"):
        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg["From"] = self.email_from
        msg["To"] = to_email

        msg.attach(MIMEText(body_html, "html"))

        part = MIMEBase("application", "pdf")
        part.set_payload(pdf_bytes)
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f'attachment; filename="{filename}"')
        msg.attach(part)

        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            server.login(self.email_user, self.email_pass)
            server.send_message(msg)