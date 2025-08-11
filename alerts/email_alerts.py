# import smtplib
# from email.mime.text import MIMEText
# import os

# def send_email_alert(subject: str, message: str):
#     host = os.getenv("EMAIL_HOST")
#     port = int(os.getenv("EMAIL_PORT", 465))
#     user = os.getenv("EMAIL_USER")
#     password = os.getenv("EMAIL_PASSWORD")
#     recipient = os.getenv("EMAIL_TO")

#     msg = MIMEText(message)
#     msg["Subject"] = subject
#     msg["From"] = user
#     msg["To"] = recipient

#     try:
#         with smtplib.SMTP_SSL(host, port) as server:
#             server.login(user, password)
#             server.send_message(msg)
#         print(f"[Email Alert] Sent to {recipient}")
#     except Exception as e:
#         print(f"[Email Alert] Failed: {e}")

# alerts/email_alerts.py
import os
import time
import smtplib
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

# Config from env
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "465"))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_TO = os.getenv("EMAIL_TO", "")
EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL", "true").lower() == "true"
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "false").lower() == "true"
EMAIL_TIMEOUT = int(os.getenv("EMAIL_TIMEOUT", "30"))
EMAIL_RETRIES = int(os.getenv("EMAIL_RETRIES", "3"))
EMAIL_RETRY_DELAY = int(os.getenv("EMAIL_RETRY_DELAY", "5"))

def _format_recipients(recipient_str):
    return [r.strip() for r in recipient_str.split(",") if r.strip()]

def send_email_alert(subject: str, message: str, to_addrs: str = None, html: bool = False):
    to_addrs = to_addrs or EMAIL_TO
    recipients = _format_recipients(to_addrs)
    if not recipients:
        print("[Email Alert] No recipient configured; skipping email.")
        return False

    # Build message
    if html:
        msg = MIMEMultipart("alternative")
        msg.attach(MIMEText(message, "html"))
    else:
        msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = ", ".join(recipients)

    last_err = None
    for attempt in range(1, EMAIL_RETRIES + 1):
        try:
            if EMAIL_USE_SSL:
                # SSL socket (port 465)
                with smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT, timeout=EMAIL_TIMEOUT) as server:
                    server.set_debuglevel(0)  # set to 1 for more verbose debugging
                    server.login(EMAIL_USER, EMAIL_PASSWORD)
                    server.sendmail(EMAIL_USER, recipients, msg.as_string())
            else:
                # Plain SMTP with optional STARTTLS (port 587 typical)
                with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT, timeout=EMAIL_TIMEOUT) as server:
                    server.set_debuglevel(0)
                    if EMAIL_USE_TLS:
                        server.starttls()  # upgrade to TLS
                    server.login(EMAIL_USER, EMAIL_PASSWORD)
                    server.sendmail(EMAIL_USER, recipients, msg.as_string())

            print(f"[Email Alert] Sent to {recipients} (attempt {attempt})")
            return True
        except (smtplib.SMTPException, socket.timeout, ConnectionRefusedError, socket.gaierror) as exc:
            last_err = exc
            print(f"[Email Alert] attempt {attempt} failed: {exc}")
            if attempt < EMAIL_RETRIES:
                time.sleep(EMAIL_RETRY_DELAY)
        except Exception as exc:
            last_err = exc
            print(f"[Email Alert] unexpected error on attempt {attempt}: {exc}")
            break

    print(f"[Email Alert] Failed after {EMAIL_RETRIES} attempts. Last error: {last_err}")
    return False
