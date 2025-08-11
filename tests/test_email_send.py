# tests/test_email_send.py
from dotenv import load_dotenv
load_dotenv()

from alerts.email_alerts import send_email_alert

if __name__ == "__main__":
    ok = send_email_alert("Test: Inventory Agent", "This is a test email from the agent.")
    print("OK:", ok)
