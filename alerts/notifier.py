import os
from alerts.email_alerts import send_email_alert
from alerts.teams_alerts import send_teams_alert

def send_alert(subject: str, message: str):
    if os.getenv("ENABLE_EMAIL_ALERTS", "false").lower() == "true":
        send_email_alert(subject, message)
    
    if os.getenv("ENABLE_TEAMS_ALERTS", "false").lower() == "true":
        send_teams_alert(f"**{subject}**\n{message}")
