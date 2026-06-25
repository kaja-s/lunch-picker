from slack_bolt import Respond
import sqlite3
import logging
from db import add_restaurant, remove_restaurant

logger = logging.getLogger(__name__)

def register_commands(app, db_conn: sqlite3.Connection):
    """
    Registers slash command handlers for the Slack app.
    """
    @app.command("/lunch")
    def handle_lunch_command(ack, body, respond: Respond):
        """
        Main entry point for /lunch slash commands.
        Routes to sub-commands based on the first word in the text.
        """
        ack()
        
        user_id = body.get("user_id")
        workspace_id = body.get("team_id")
        text = body.get("text", "").strip()
        
        logger.info(f"Received /lunch command from user {user_id} in workspace {workspace_id} with text: '{text}'")

        if not text:
            respond("Welcome to Lunch Picker! Use `/lunch add`, `/lunch list`, or `/lunch pick`.")
            return

        parts = text.split(maxsplit=2)
        subcommand = parts[0].lower()

        if subcommand == "add":
            if len(parts) < 3:
                respond("Usage: /lunch add <name> <address>")
                return
            
            name = parts[1]
            address = parts[2]
            
            try:
                add_restaurant(db_conn, workspace_id, name, address)
                respond(f"Added restaurant: *{name}* at {address}")
            except ValueError as e:
                respond(str(e))
            except Exception as e:
                logger.error(f"Error adding restaurant: {e}")
                respond("An internal error occurred while adding the restaurant.")
        elif subcommand == "remove":
            if len(parts) < 2:
                respond("Usage: /lunch remove <name>")
                return
            
            name = parts[1]
            try:
                if remove_restaurant(db_conn, workspace_id, name):
                    respond(f"Removed restaurant: *{name}*")
                else:
                    respond(f"Restaurant '{name}' not found.")
            except Exception as e:
                logger.error(f"Error removing restaurant: {e}")
                respond("An internal error occurred while removing the restaurant.")
        elif subcommand == "list":
            try:
                from db import list_restaurants
                restaurants = list_restaurants(db_conn, workspace_id)
                if not restaurants:
                    respond("No restaurants have been added yet.")
                else:
                    lines = [f"• *{name}*: {address}" for name, address in restaurants]
                    respond("Here are the restaurants in your list:\n" + "\n".join(lines))
            except Exception as e:
                logger.error(f"Error listing restaurants: {e}")
                respond("An internal error occurred while listing restaurants.")
        elif subcommand == "pick":
            try:
                from db import pick_restaurant
                result = pick_restaurant(db_conn, workspace_id)
                if not result:
                    respond("No restaurants have been added yet.")
                else:
                    name, address = result
                    respond(f"How about: *{name}*? It's at {address}")
            except Exception as e:
                logger.error(f"Error picking restaurant: {e}")
                respond("An internal error occurred while picking a restaurant.")
        else:
            respond(f"Unknown command: {subcommand}. Use `/lunch add`, `/lunch list`, or `/lunch pick`.")