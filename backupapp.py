from flask import Flask, request, jsonify
import os
from slack_sdk import WebClient

app = Flask(__name__)
slack_client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))

@app.route('/slack/meeting', methods=['POST'])
def create_meeting():
    data = request.form.to_dict() or request.json  # Handle both forms & JSON
    print("🚀 Incoming Slack Data:", data)

    if "command" in data:  # Slash command
        user_id = data.get('user_id', 'Unknown User')
        channel_id = data.get('channel_id', 'Unknown Channel')
        text = data.get('text', '')

        if not text:
            return jsonify({"text": "Error: Please provide a meeting name.", "response_type": "ephemeral"})

        meeting_name = " ".join(text.split())
        response_text = f"Creating Google Meet for: {meeting_name}"

        slack_client.chat_postMessage(channel=channel_id, text=response_text)

        return jsonify({"text": response_text, "response_type": "in_channel"})

    elif "event" in data:  # Slack Event Subscription
        event = data["event"]
        if event.get("type") == "message" and not event.get("subtype"):  # Ignore bot messages
            slack_client.chat_postMessage(channel=event["channel"], text="Hey! I'm your Meet bot!")

        return jsonify({"ok": True})  # Acknowledge Slack event

    return jsonify({"error": "Invalid request"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

