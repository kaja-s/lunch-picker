import pytest
from unittest.mock import MagicMock
from commands import register_commands

class MockRespond:
    def __init__(self):
        self.calls = []
    def __call__(self, text):
        self.calls.append(text)

def test_lunch_command_no_args():
    """
    Test /lunch with no arguments.
    """
    # Setup mock app and db
    mock_app = MagicMock()
    mock_db = MagicMock()
    # The decorator @app.command("/lunch") calls app.command("/lunch")(handler)
    # We make the first call return a mock that captures the handler
    handler_captor = MagicMock()
    mock_app.command.return_value = handler_captor
    
    register_commands(mock_app, mock_db)
    
    # Extract the handler function passed to the decorator
    handler_func = handler_captor.call_args[0][0]
    
    ack = MagicMock()
    respond = MockRespond()
    body = {
        "user_id": "U123",
        "team_id": "T123",
        "text": ""
    }
    
    handler_func(ack, body, respond)
    
    ack.assert_called_once()
    assert "Welcome to Lunch Picker!" in respond.calls[0]

def test_lunch_add_missing_args():
    """Verify usage message when arguments are missing."""
    mock_app = MagicMock()
    mock_db = MagicMock()
    handler_captor = MagicMock()
    mock_app.command.return_value = handler_captor
    register_commands(mock_app, mock_db)
    handler_func = handler_captor.call_args[0][0]

    respond = MockRespond()
    body = {"team_id": "T1", "text": "add OnlyName"}
    
    handler_func(MagicMock(), body, respond)
    assert "Usage: /lunch add <name> <address>" in respond.calls[0]

def test_lunch_add_success():
    """Verify successful addition of a restaurant via slash command."""
    from db import initialize_db
    # Use a real in-memory DB for integration-like unit test of the command
    conn = initialize_db(":memory:")
    
    mock_app = MagicMock()
    handler_captor = MagicMock()
    mock_app.command.return_value = handler_captor
    register_commands(mock_app, conn)
    handler_func = handler_captor.call_args[0][0]

    respond = MockRespond()
    body = {"team_id": "T1", "text": "add PizzaPlace 123_Main_St"}
    
    handler_func(MagicMock(), body, respond)
    
    assert "Added restaurant: *PizzaPlace* at 123_Main_St" in respond.calls[0]
    
    # Verify DB state
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM restaurants WHERE workspace_id='T1'")
    assert cursor.fetchone()["name"] == "PizzaPlace"

def test_lunch_add_duplicate():
    """Verify error message when adding a duplicate restaurant."""
    from db import initialize_db, add_restaurant
    conn = initialize_db(":memory:")
    add_restaurant(conn, "T1", "Existing", "Addr")
    
    mock_app = MagicMock()
    handler_captor = MagicMock()
    mock_app.command.return_value = handler_captor
    register_commands(mock_app, conn)
    handler_func = handler_captor.call_args[0][0]

    respond = MockRespond()
    body = {"team_id": "T1", "text": "add Existing NewAddr"}
    
    handler_func(MagicMock(), body, respond)
    assert "already exists" in respond.calls[0].lower()

def test_lunch_remove_missing_args():
    """Verify usage message when name is missing for remove."""
    mock_app = MagicMock()
    mock_db = MagicMock()
    handler_captor = MagicMock()
    mock_app.command.return_value = handler_captor
    register_commands(mock_app, mock_db)
    handler_func = handler_captor.call_args[0][0]

    respond = MockRespond()
    body = {"team_id": "T1", "text": "remove"}
    
    handler_func(MagicMock(), body, respond)
    assert "Usage: /lunch remove <name>" in respond.calls[0]

def test_lunch_remove_not_found():
    """Verify response when trying to remove a non-existent restaurant."""
    from db import initialize_db
    conn = initialize_db(":memory:")
    
    mock_app = MagicMock()
    handler_captor = MagicMock()
    mock_app.command.return_value = handler_captor
    register_commands(mock_app, conn)
    handler_func = handler_captor.call_args[0][0]

    respond = MockRespond()
    body = {"team_id": "T1", "text": "remove GhostResto"}
    
    handler_func(MagicMock(), body, respond)
    assert "not found" in respond.calls[0].lower()

def test_lunch_remove_success():
    """Verify successful removal of a restaurant via slash command."""
    from db import initialize_db, add_restaurant
    conn = initialize_db(":memory:")
    add_restaurant(conn, "T1", "ToDelete", "Address")
    
    mock_app = MagicMock()
    handler_captor = MagicMock()
    mock_app.command.return_value = handler_captor
    register_commands(mock_app, conn)
    handler_func = handler_captor.call_args[0][0]

    respond = MockRespond()
    body = {"team_id": "T1", "text": "remove ToDelete"}
    
    handler_func(MagicMock(), body, respond)
    assert "Removed restaurant: *ToDelete*" in respond.calls[0]
    
    # Verify DB state
    from db import list_restaurants
    assert len(list_restaurants(conn, "T1")) == 0

def test_lunch_list_empty():
    """Verify response when listing an empty restaurant list."""
    from db import initialize_db
    conn = initialize_db(":memory:")
    
    mock_app = MagicMock()
    handler_captor = MagicMock()
    mock_app.command.return_value = handler_captor
    register_commands(mock_app, conn)
    handler_func = handler_captor.call_args[0][0]

    respond = MockRespond()
    body = {"team_id": "T1", "text": "list"}
    
    handler_func(MagicMock(), body, respond)
    assert "no restaurants have been added yet" in respond.calls[0].lower()

def test_lunch_list_success():
    """Verify response when listing multiple restaurants."""
    from db import initialize_db, add_restaurant
    conn = initialize_db(":memory:")
    add_restaurant(conn, "T1", "Burger Joint", "1st Street")
    add_restaurant(conn, "T1", "Salad Bar", "2nd Avenue")
    
    mock_app = MagicMock()
    handler_captor = MagicMock()
    mock_app.command.return_value = handler_captor
    register_commands(mock_app, conn)
    handler_func = handler_captor.call_args[0][0]

    respond = MockRespond()
    body = {"team_id": "T1", "text": "list"}
    
    handler_func(MagicMock(), body, respond)
    
    response_text = respond.calls[0]
    assert "Burger Joint" in response_text
    assert "1st Street" in response_text
    assert "Salad Bar" in response_text
    assert "2nd Avenue" in response_text

def test_lunch_pick_empty():
    """Verify response when picking from an empty list."""
    from db import initialize_db
    conn = initialize_db(":memory:")
    
    mock_app = MagicMock()
    handler_captor = MagicMock()
    mock_app.command.return_value = handler_captor
    register_commands(mock_app, conn)
    handler_func = handler_captor.call_args[0][0]

    respond = MockRespond()
    body = {"team_id": "T1", "text": "pick"}
    
    handler_func(MagicMock(), body, respond)
    assert "no restaurants have been added yet" in respond.calls[0].lower()

def test_lunch_pick_success():
    """Verify response when picking returns a restaurant."""
    from db import initialize_db, add_restaurant
    conn = initialize_db(":memory:")
    add_restaurant(conn, "T1", "Target Resto", "Target Addr")
    
    mock_app = MagicMock()
    handler_captor = MagicMock()
    mock_app.command.return_value = handler_captor
    register_commands(mock_app, conn)
    handler_func = handler_captor.call_args[0][0]

    respond = MockRespond()
    body = {"team_id": "T1", "text": "pick"}
    
    handler_func(MagicMock(), body, respond)
    
    response_text = respond.calls[0]
    assert "How about: *Target Resto*" in response_text
    assert "Target Addr" in response_text