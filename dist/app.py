import os
import logging
from slack_bolt import App
from db import initialize_db
from commands import handle_lunch_command

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration from environment
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.environ.get("SLACK_SIGNING_SECRET")
PORT = int(os.environ.get("PORT", 3000))
DB_PATH = os.environ.get("DB_PATH", "lunch.db")

if not SLACK_BOT_TOKEN or not SLACK_SIGNING_SECRET:
    raise ValueError("SLACK_BOT_TOKEN and SLACK_SIGNING_SECRET must be set in environment.")

# Initialize Bolt App
app = App(
    token=SLACK_BOT_TOKEN,
    signing_secret=SLACK_SIGNING_SECRET
)

# Initialize Database
db_conn = initialize_db(DB_PATH)

@app.command("/lunch")
def lunch_command(ack, body, respond):
    """Routes the /lunch slash command to the logic handler."""
    handle_lunch_command(ack, body, respond, db_conn)

if __name__ == "__main__":
    logger.info(f"Starting Slack bot on port {PORT}...")
    app.start(port=PORT)