import os
import logging
from slack_bolt import App
from db import initialize_db
from commands import register_commands

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize Slack Bolt App
# Signing secret is required for HTTP mode (Request Verification)
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
    token_verification_enabled=False
)

# Initialize Database
db_path = os.environ.get("LUNCH_PICKER_DB", "lunch_picker.db")
db_conn = None
try:
    db_conn = initialize_db(db_path)
except Exception as e:
    logger.error(f"Fatal error: Could not initialize database: {e}")
    exit(1)

# Register Slash Command Handlers
register_commands(app, db_conn)

if __name__ == "__main__":
    # Start the app using the built-in HTTP server
    port = int(os.environ.get("PORT", 3000))
    
    if not os.environ.get("SLACK_BOT_TOKEN"):
        logger.error("Environment variable SLACK_BOT_TOKEN is missing.")
    if not os.environ.get("SLACK_SIGNING_SECRET"):
        logger.error("Environment variable SLACK_SIGNING_SECRET is missing.")
        
    logger.info(f"Starting Lunch Picker bot on port {port}")
    app.start(port=port)