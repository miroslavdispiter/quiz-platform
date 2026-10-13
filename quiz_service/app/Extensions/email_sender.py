import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import Config


class EmailSender:

    def send_quiz_result_email(self, to_email, full_name, quiz_title, score, max_score, time_spent) -> bool:
        """Sends the player the result of a processed quiz. Returns True if the mail was sent."""
        if not Config.EMAIL_USER or not Config.EMAIL_PASS:
            print("Email is not configured (EMAIL_USER / EMAIL_PASS in .env) - mail is not sent.")
            return False

        percentage = round(score / max_score * 100, 2) if max_score > 0 else 0

        subject = f"Quiz result: {quiz_title}"
        body = (
            f"Dear {full_name},<br><br>"
            f"Your quiz <b>{quiz_title}</b> has been processed.<br><br>"
            f"Points: <b>{score} / {max_score}</b> ({percentage}%)<br>"
            f"Time spent: <b>{time_spent} s</b><br><br>"
            f"Best regards,<br>Quiz Platform Team"
        )

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = Config.EMAIL_FROM
        msg["To"] = to_email
        msg.attach(MIMEText(body, "html"))

        with smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT) as server:
            server.starttls()
            server.login(Config.EMAIL_USER, Config.EMAIL_PASS)
            server.send_message(msg)
        return True
