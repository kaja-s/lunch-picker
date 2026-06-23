import os
import logging
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from db import initialize_db
from commands import handle_lunch_command

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """
    Factory function to initialize the Slack Bolt App and database.
    """
    # Environment variables
    token = os.environ.get("SLACK_BOT_TOKEN")
    signing_secret = os.environ.get("SLACK_SIGNING_SECRET")
    db_path = os.environ.get("DATABASE_PATH", "lunch_bot.db")
    
    if not token or not signing_secret:
        error_msg = "Missing SLACK_BOT_TOKEN or SLACK_SIGNING_SECRET in environment variables."
        logger.error(error_msg)
        raise EnvironmentError(error_msg)

    # Initialize Database
    try:
        conn = initialize_db(db_path)
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

    # Initialize Bolt App
    # We use the standard HTTP server adapter by default
    app = App(
        token=token,
        signing_secret=signing_secret
    )

    # Register command handlers
    # Use a lambda to inject the database connection into the handler
    @app.command("/lunch")
    def lunch_command(ack, body, respond):
        handle_lunch_command(ack, body, respond, conn)

    return app

if __name__ == "__main__":
    # Get port from environment or default to 3000
    port = int(os.environ.get("PORT", 3000))
    
    try:
        bolt_app = create_app()
        logger.info(f"Starting Slack Bot server on port {port}...")
        bolt_app.start(port=port)
    except Exception as e:
        logger.critical(f"App failed to start: {e}", exc_info=True)
        exit(1)