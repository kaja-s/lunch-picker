import os
import logging
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from db import init_db
from commands import handle_lunch_command

# Configuration
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.environ.get("SLACK_SIGNING_SECRET")
PORT = int(os.environ.get("PORT", 3000))

# Initialize Logger
logging.basicConfig(level=logging.INFO)

# Check for required environment variables
if not SLACK_BOT_TOKEN or not SLACK_SIGNING_SECRET:
    raise RuntimeError("SLACK_BOT_TOKEN and SLACK_SIGNING_SECRET must be set.")

app = App(token=SLACK_BOT_TOKEN, signing_secret=SLACK_SIGNING_SECRET)

# Register command handler
app.command("/lunch")(handle_lunch_command)

if __name__ == "__main__":
    init_db()
    # Starting standard HTTP server (Bolt default)
    # Using start() for HTTP mode as per standard Bolt usage
    app.start(port=PORT)