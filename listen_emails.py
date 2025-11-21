import requests
import time
from datetime import datetime

MAILHOG_API = "http://localhost:8025/api/v2/messages"
CHECK_INTERVAL = 2  # seconds

seen_message_ids = set()

def check_new_emails():
    try:
        response = requests.get(MAILHOG_API)
        response.raise_for_status()
        data = response.json()
        
        messages = data.get("items", [])
        
        for msg in messages:
            msg_id = msg["ID"]
            if msg_id not in seen_message_ids:
                seen_message_ids.add(msg_id)
                
                # Extract email details
                from_addr = msg["From"]["Mailbox"] + "@" + msg["From"]["Domain"]
                to_addr = msg["To"][0]["Mailbox"] + "@" + msg["To"][0]["Domain"]
                subject = msg["Content"]["Headers"]["Subject"][0]
                
                print(f"\n🔔 New email received at {datetime.now().strftime('%H:%M:%S')}")
                print(f"   From: {from_addr}")
                print(f"   To: {to_addr}")
                print(f"   Subject: {subject}")
                print(f"   Message ID: {msg_id}")
                
                # YOUR CALLBACK LOGIC HERE
                handle_new_email(msg)
                
    except Exception as e:
        print(f"Error checking emails: {e}")

def handle_new_email(message):
    """Your custom callback logic goes here"""
    # Process the email message
    # Example: save to database, trigger workflow, send notification, etc.
    pass

if __name__ == "__main__":
    print(f"👀 Listening for new emails (checking every {CHECK_INTERVAL}s)...")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            check_new_emails()
            time.sleep(CHECK_INTERVAL)
    except KeyboardInterrupt:
        print("\n\n✓ Stopped listening")
