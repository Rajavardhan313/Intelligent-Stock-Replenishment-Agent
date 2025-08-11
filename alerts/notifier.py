# import os
# from alerts.email_alerts import send_email_alert
# from alerts.teams_alerts import send_teams_alert

# def send_alert(subject: str, message: str):
#     if os.getenv("ENABLE_EMAIL_ALERTS", "false").lower() == "true":
#         send_email_alert(subject, message)
    
#     if os.getenv("ENABLE_TEAMS_ALERTS", "false").lower() == "true":
#         send_teams_alert(f"**{subject}**\n{message}")

# alerts/notifier.py
import os
from alerts.email_alerts import send_email_alert
from alerts.teams_alerts import send_teams_alert

def send_alert(subject: str, message: str):
    # Teams alert
    if os.getenv("ENABLE_TEAMS_ALERTS", "false").lower() == "true":
        try:
            send_teams_alert(f"**{subject}**\n{message}")
        except Exception as e:
            print(f"[Notifier] Teams failed: {e}")

    # Email alert
    if os.getenv("ENABLE_EMAIL_ALERTS", "false").lower() == "true":
        try:
            ok = send_email_alert(subject, message)
            if not ok:
                print("[Notifier] Email send failed — check logs / network.")
        except Exception as e:
            print(f"[Notifier] Email failed: {e}")