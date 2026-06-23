import logging
from typing import Any, Callable
from db import add_restaurant, remove_restaurant, list_restaurants, pick_restaurant

logger = logging.getLogger(__name__)

def handle_lunch_command(ack: Callable, body: dict[str, Any], respond: Callable, conn: Any) -> None:
    """
    Main dispatcher for the /lunch slash command.
    """
    ack()
    
    text = body.get("text", "").strip()
    workspace_id = body.get("team_id")
    
    if not workspace_id:
        respond("Error: Could not identify workspace ID.")
        return

    parts = text.split(maxsplit=2)
    subcommand = parts[0].lower() if len(parts) > 0 else ""

    try:
        if subcommand == "add":
            if len(parts) < 3:
                respond("Usage: /lunch add <name> <address>")
                return
            name, address = parts[1].strip(), parts[2].strip()
            if not name or not address:
                respond("Usage: /lunch add <name> <address>")
                return
            add_restaurant(conn, workspace_id, name, address)
            respond(f"Added restaurant: *{name}* ({address})")

        elif subcommand == "remove":
            if len(parts) < 2:
                respond("Usage: /lunch remove <name>")
                return
            name = parts[1].strip()
            if not name:
                respond("Usage: /lunch remove <name>")
                return
            deleted = remove_restaurant(conn, workspace_id, name)
            if deleted:
                respond(f"Removed restaurant: *{name}*")
            else:
                respond(f"Restaurant *{name}* not found in your list.")

        elif subcommand == "list":
            items = list_restaurants(conn, workspace_id)
            if not items:
                respond("No restaurants have been added yet.")
            else:
                formatted_list = "\n".join([f"• *{name}*: {addr}" for name, addr in items])
                respond(f"Here are your restaurants:\n{formatted_list}")

        elif subcommand == "pick":
            picked = pick_restaurant(conn, workspace_id)
            if not picked:
                respond("The restaurant list is empty. Add some restaurants first!")
            else:
                name, addr = picked
                respond(f"Today's lunch recommendation is: *{name}* ({addr})")

        else:
            respond("Unknown command. Available sub-commands: `add`, `remove`, `list`, `pick`.")

    except ValueError as e:
        respond(f"Error: {str(e)}")
    except Exception as e:
        error_msg = f"An unexpected error occurred: {str(e)}"
        logger.exception(error_msg)
        respond(error_msg)