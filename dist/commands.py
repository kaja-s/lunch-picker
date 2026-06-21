import random
from db import add_restaurant, list_restaurants, remove_restaurant

def handle_lunch_command(ack, body, say):
    ack()
    text = body.get("text", "").strip()
    workspace_id = body.get("team_id")
    
    if not text:
        say("Usage: `/lunch add <name> <address>`, `/lunch list`, `/lunch pick`, or `/lunch remove <name>`")
        return

    parts = text.split(maxsplit=2)
    subcommand = parts[0].lower()

    try:
        if subcommand == "add":
            if len(parts) < 3:
                say("Usage: /lunch add <name> <address>")
                return
            name, address = parts[1], parts[2]
            add_restaurant(workspace_id, name, address)
            say(f"Added *{name}* ({address}) to the lunch list.")

        elif subcommand == "list":
            restaurants = list_restaurants(workspace_id)
            if not restaurants:
                say("No restaurants have been added yet.")
            else:
                resp = "\n".join([f"• *{r['name']}* - {r['address']}" for r in restaurants])
                say(f"Here are the restaurants:\n{resp}")

        elif subcommand == "remove":
            if len(parts) < 2:
                say("Usage: /lunch remove <name>")
                return
            name = parts[1]
            if remove_restaurant(workspace_id, name):
                say(f"Removed *{name}* from the lunch list.")
            else:
                say(f"Restaurant *{name}* not found in the lunch list.")

        elif subcommand == "pick":
            restaurants = list_restaurants(workspace_id)
            if not restaurants:
                say("No restaurants have been added yet.")
            else:
                choice = random.choice(restaurants)
                say(f"Today's lunch spot: *{choice['name']}* ({choice['address']})")
        
        else:
            say(f"Unknown subcommand: `{subcommand}`. Try `add`, `list`, `pick`, or `remove`.")

    except Exception as e:
        say(f"An error occurred: {str(e)}")