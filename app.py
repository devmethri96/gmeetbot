from flask import Flask, request, jsonify
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os
import uuid
import logging
import pickle
import datetime
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ✅ Initialize Flask app (Fixes the NameError issue)
app = Flask(__name__)

# ✅ Load Slack Bot Token
slack_client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))

# ✅ Google OAuth Scope for Google Meet
SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

# ✅ Function to Load/Refresh Google Credentials
def get_google_service():
    creds = None

    # 🔍 Load existing credentials if available
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token_file:
            creds = pickle.load(token_file)

    # 🔄 Check if credentials need refreshing
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())  # 🔄 Refresh token automatically
        with open("token.pickle", "wb") as token_file:  # ✅ Save refreshed token
            pickle.dump(creds, token_file)

    # 🔄 If credentials are not valid (missing or expired without refresh token), re-authenticate
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
        creds = flow.run_console()  # Manual re-auth if no valid token
        with open("token.pickle", "wb") as token_file:  # ✅ Save new token
            pickle.dump(creds, token_file)

    return build("calendar", "v3", credentials=creds)


# ✅ Function to Generate Google Meet Link
def generate_meet_link(event_name):
    service = get_google_service()
    if not service:
        logging.error("❌ Google authentication failed. Please re-authenticate.")
        return None  # No valid token available

    request_id = str(uuid.uuid4())  # Unique request ID

    # 🔥 Set event start time dynamically (30 mins from now)
    start_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    end_time = start_time + datetime.timedelta(hours=1)

    event = {
        "summary": event_name,
        "conferenceData": {
            "createRequest": {
                "requestId": request_id,
                "conferenceSolutionKey": {"type": "hangoutsMeet"}
            }
        },
        "start": {"dateTime": start_time.isoformat() + "Z", "timeZone": "UTC"},
        "end": {"dateTime": end_time.isoformat() + "Z", "timeZone": "UTC"},
    }

    try:
        created_event = service.events().insert(
            calendarId="primary",
            body=event,
            conferenceDataVersion=1
        ).execute()

        return created_event.get("hangoutLink")

    except Exception as e:
        logging.error(f"❌ Google Meet API Error: {str(e)}")
        return None

# ✅ Slack Command Handler
@app.route("/slack/meeting", methods=["POST"])
def create_meeting():
    data = request.form
    user_id = data.get("user_id")
    text = data.get("text")  # Meeting name

    if not text:
        return jsonify({"text": "⚠️ Error: Please provide a meeting name."})

    meet_link = generate_meet_link(text)

    if not meet_link:
        return jsonify({"text": "❌ Error: Unable to generate Google Meet link. Try re-authenticating."})

    message = (
        f"👋 Hey <@{user_id}>, your meeting is ready!\n"
        f"🔗 Google Meet: {meet_link}"
    )

    try:
        slack_client.chat_postMessage(channel=user_id, text=message)
    except SlackApiError as e:
        return jsonify({"text": f"❌ Slack error: {e.response['error']}"})

    return "", 200

# ✅ Run Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

