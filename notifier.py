import os
import requests
from dotenv import load_dotenv

load_dotenv()
SLACK_WEBHOOK = os.getenv('SLACK_WEBHOOK_URL')

def send_slack_message(text):
    if not SLACK_WEBHOOK:
        print("No SLACK_WEBHOOK configured, printing instead:\n", text)
        return
    requests.post(SLACK_WEBHOOK, json={"text": text})
