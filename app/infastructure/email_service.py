import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from celery import shared_task
from app.infastructure.config import EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, EMAIL_USE_TLS
import logging

@shared_task
def send_email_task(subject: str, recipient: str, message: str):
    """Send an email asynchronously using Celery."""
    try:
        print(f"📧 [Celery] Sending email to {recipient} with subject '{subject}'")
        logging.info(f"📧 [Celery] Sending email to {recipient} with subject '{subject}'")

        msg = MIMEMultipart()
        msg["From"] = EMAIL_HOST_USER
        msg["To"] = recipient
        msg["Subject"] = subject
        msg.attach(MIMEText(message, "plain"))

        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT, timeout=10)
        print("📧 [Celery] Connected to SMTP server")
        if EMAIL_USE_TLS:
            server.starttls()
            print("📧 [Celery] TLS started")

        server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        print("📧 [Celery] Logged in to SMTP")
        
        server.sendmail(EMAIL_HOST_USER, recipient, msg.as_string())
        print(f"✅ [Celery] Email successfully sent to {recipient}")
        server.quit()

        return {"status": "Email sent", "recipient": recipient}

    except Exception as e:
        print(f"❌ [Celery] Error sending email: {e}")
        logging.error(f"❌ [Celery] Error sending email: {e}")
        return {"error": str(e)}
