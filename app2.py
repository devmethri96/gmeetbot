from flask import Flask, request, jsonify
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os
import uuid
import logging
import google.auth
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import pickle

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey")

slack_client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))

# ✅ Correct Scope for Meet Link Generation
SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

# ✅ Function to Load or Get New Google Credentials
def get_google_service():
    creds = None

    # Load saved credentials (if available)
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token_file:
            creds = pickle.load(token_file)

    # If no credentials or expired, re-authenticate
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
        creds = flow.run_console()  # Terminal-based authentication

        # Save credentials for future use
        with open("token.pickle", "wb") as token_file:
            pickle.dump(creds, token_file)

    return build("calendar", "v3", credentials=creds)

# ✅ Function to Generate Google Meet Link
def generate_meet_link(event_name):
    try:
        logging.debug("🔍 Loading Google OAuth credentials...")
        service = get_google_service()

        request_id = str(uuid.uuid4())  # Unique ID
        logging.debug(f"📌 Creating event with request ID: {request_id}")

        event = {
            "summary": event_name,
            "conferenceData": {
                "createRequest": {
                    "requestId": request_id,
                    "conferenceSolutionKey": {"type": "hangoutsMeet"}
                }
            },
            "start": {"dateTime": "2025-03-28T10:00:00Z", "timeZone": "UTC"},
            "end": {"dateTime": "2025-03-28T11:00:00Z", "timeZone": "UTC"},
        }

        created_event = service.events().insert(
            calendarId="primary",
            body=event,
            conferenceDataVersion=1
        ).execute()

        meet_link = created_event.get("hangoutLink")
        logging.debug(f"✅ Meet link generated: {meet_link}")
        return meet_link

    except Exception as e:
        logging.error(f"❌ Google Meet API Error: {str(e)}")  # Log errors
        return None

# ✅ Slack Command Handler
@app.route("/slack/meeting", methods=["POST"])
def create_meeting():
    data = request.form
    user_id = data.get("user_id")
    text = data.get("text")  # Event name

    if not text:
        return jsonify({"text": "⚠️ Error: Please provide a meeting name."})

    meet_link = generate_meet_link(text)

    if not meet_link:
        return jsonify({"text": "❌ Error: Unable to generate Google Meet link."})

    message = (
        f"👋 Hey <@{user_id}>, ready to start your meeting?\n"
        f"🔗 Google Meet link: {meet_link}"
    )

    try:
        slack_client.chat_postMessage(channel=user_id, text=message)
    except SlackApiError as e:
        return jsonify({"text": f"❌ Error sending message: {e.response['error']}"})

    return "", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

