import logging
from slack_bolt import Respond
from sqlite3 import Connection

logger = logging.getLogger(__name__)

def handle_lunch_command(ack, body, respond: Respond, conn: Connection):
    """
    Main dispatcher for the /lunch slash command.
    """
    # Acknowledge the command immediately as required by Slack API
    ack()
    
    text = body.get("text", "").strip()
    user_id = body.get("user_id")
    workspace_id = body.get("team_id")
    
    logger.info(f"Received /lunch command from user {user_id} in workspace {workspace_id} with text: '{text}'")

    if not text:
        respond("Welcome to Lunch Bot! Use `/lunch help` to see available commands.")
        return

    # Basic routing logic for sub-commands
    parts = text.split(maxsplit=1)
    subcommand = parts[0].lower()
    remaining_text = parts[1] if len(parts) > 1 else ""

    if subcommand == "add":
        # Expecting: /lunch add <name> <address>
        # We use maxsplit=1 on remaining_text to get name and address
        args = remaining_text.split(maxsplit=1)
        if len(args) < 2:
            respond("Usage: /lunch add <name> <address>")
            return

        name, address = args[0], args[1]
        try:
            from db import add_restaurant
            add_restaurant(conn, workspace_id, name, address)
            respond(f"Added restaurant: *{name}* at {address}")
        except ValueError as e:
            # Check if it's the duplicate name error defined in db.py
            if "already exists" in str(e):
                respond(f"Error: Restaurant '{name}' already exists in this workspace.")
            else:
                respond(f"Error: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to add restaurant: {e}", exc_info=True)
            respond(f"An unexpected error occurred while adding the restaurant: {str(e)}")
        return

    if subcommand == "list":
        try:
            from db import list_restaurants
            restaurants = list_restaurants(conn, workspace_id)
            if not restaurants:
                respond("No restaurants have been added yet.")
            else:
                formatted_list = "\n".join([f"• *{name}*: {address}" for name, address in restaurants])
                respond(f"Here are the restaurants in your list:\n{formatted_list}")
        except Exception as e:
            logger.error(f"Failed to list restaurants: {e}", exc_info=True)
            respond(f"An unexpected error occurred while listing restaurants: {str(e)}")
        return

    if subcommand == "remove":
        # Expecting: /lunch remove <name>
        name = remaining_text.strip()
        if not name:
            respond("Usage: /lunch remove <name>")
            return

        try:
            from db import remove_restaurant
            if remove_restaurant(conn, workspace_id, name):
                respond(f"Removed restaurant: *{name}*")
            else:
                respond(f"Error: Restaurant '{name}' was not found.")
        except Exception as e:
            logger.error(f"Failed to remove restaurant: {e}", exc_info=True)
            respond(f"An unexpected error occurred while removing the restaurant: {str(e)}")
        return

    if subcommand == "pick":
        try:
            from db import pick_restaurant
            picked = pick_restaurant(conn, workspace_id)
            if not picked:
                respond("No restaurants have been added yet.")
            else:
                name, address = picked
                respond(f"How about *{name}*?\nAddress: {address}")
        except Exception as e:
            logger.error(f"Failed to pick restaurant: {e}", exc_info=True)
            respond(f"An unexpected error occurred while picking a restaurant: {str(e)}")
        return

    respond(f"Command '{subcommand}' received. This functionality is being implemented.")