import os
import requests
from flask import Flask, request, jsonify
from slack_sdk import WebClient
from urllib.parse import quote_plus

# Load Slack Token
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
slack_client = WebClient(token=SLACK_BOT_TOKEN)

app = Flask(__name__)

@app.route("/slack/meeting", methods=["POST"])
def create_meeting():
    user_id = request.form.get("user_id")
    channel_id = request.form.get("channel_id")
    text = request.form.get("text")  

    # Extract meeting topic and invitees
    parts = text.split()
    meeting_topic = parts[0] if parts else "Slack Meeting"
    invitees = [part.replace("@", "") + "@example.com" for part in parts[1:]]

    # Generate Google Meet link (public API workaround)
    meet_link = f"https://meet.google.com/new"

    # Generate Google Calendar event link for the user
    event_link = f"https://calendar.google.com/calendar/render?action=TEMPLATE&text={quote_plus(meeting_topic)}&details=Meeting%20Link:%20{quote_plus(meet_link)}&location={quote_plus(meet_link)}"

    # Send response to Slack
    message = f"""
    <@{user_id}>, here is your Google Meet link: {meet_link}
    📅 Click [here]({event_link}) to add this to your Google Calendar!
    """
    
    slack_client.chat_postMessage(
        channel=channel_id,
        text=message,
        unfurl_links=True
    )

    return jsonify({"status": "success"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
