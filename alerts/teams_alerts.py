import requests
import os

def send_teams_alert(message: str):
    webhook_url = os.getenv("TEAMS_WEBHOOK_URL")
    if not webhook_url:
        print("[Teams Alert] No webhook URL configured")
        return

    payload = {"text": message}
    try:
        response = requests.post(webhook_url, json=payload)
        if response.status_code == 200:
            print("[Teams Alert] Sent successfully")
        else:
            print(f"[Teams Alert] Failed: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"[Teams Alert] Error: {e}")
