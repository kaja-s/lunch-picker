import pytest
from unittest.mock import MagicMock
from commands import handle_lunch_command
from db import initialize_db

class RespondStub:
    """Stub to capture calls to the Slack respond utility."""
    def __init__(self):
        self.calls = []
    
    def __call__(self, text):
        self.calls.append(text)

@pytest.fixture
def db_conn():
    conn = initialize_db(":memory:")
    yield conn
    conn.close()

def test_handle_lunch_add(db_conn):
    respond = RespondStub()
    ack = MagicMock()
    body = {
        "team_id": "T123",
        "text": "add BurgerJoint http://burger.com"
    }
    
    handle_lunch_command(ack, body, respond, db_conn)
    
    ack.assert_called_once()
    assert "Added restaurant: *BurgerJoint*" in respond.calls[0]

def test_handle_lunch_add_missing_args(db_conn):
    respond = RespondStub()
    ack = MagicMock()
    # Missing address
    body = {"team_id": "T123", "text": "add OnlyName"}
    
    handle_lunch_command(ack, body, respond, db_conn)
    assert respond.calls[0] == "Usage: /lunch add <name> <address>"

def test_handle_lunch_remove_success(db_conn):
    from db import add_restaurant
    add_restaurant(db_conn, "T123", "OldPlace", "Addr")
    
    respond = RespondStub()
    ack = MagicMock()
    body = {"team_id": "T123", "text": "remove OldPlace"}
    
    handle_lunch_command(ack, body, respond, db_conn)
    assert "Removed restaurant: *OldPlace*" in respond.calls[0]

def test_handle_lunch_remove_missing_args(db_conn):
    respond = RespondStub()
    ack = MagicMock()
    body = {"team_id": "T123", "text": "remove   "}
    
    handle_lunch_command(ack, body, respond, db_conn)
    assert respond.calls[0] == "Usage: /lunch remove <name>"

def test_handle_lunch_remove_not_found(db_conn):
    respond = RespondStub()
    ack = MagicMock()
    body = {"team_id": "T123", "text": "remove GhostRestaurant"}
    
    handle_lunch_command(ack, body, respond, db_conn)
    assert "GhostRestaurant* not found" in respond.calls[0]

def test_handle_lunch_add_duplicate(db_conn):
    from db import add_restaurant
    add_restaurant(db_conn, "T123", "Repeat", "Addr")
    
    respond = RespondStub()
    ack = MagicMock()
    body = {"team_id": "T123", "text": "add Repeat NewAddr"}
    
    handle_lunch_command(ack, body, respond, db_conn)
    assert "already exists" in respond.calls[0].lower()

def test_handle_lunch_list_empty(db_conn):
    respond = RespondStub()
    ack = MagicMock()
    body = {"team_id": "T123", "text": "list"}
    
    handle_lunch_command(ack, body, respond, db_conn)
    
    assert respond.calls[0] == "No restaurants have been added yet."

def test_handle_lunch_pick_success(db_conn):
    from db import add_restaurant
    add_restaurant(db_conn, "T123", "Sushi Place", "123 Fish St")
    
    respond = RespondStub()
    ack = MagicMock()
    body = {"team_id": "T123", "text": "pick"}
    
    handle_lunch_command(ack, body, respond, db_conn)
    
    ack.assert_called_once()
    assert "Today's lunch recommendation is: *Sushi Place* (123 Fish St)" in respond.calls[0]

def test_handle_lunch_pick_isolation(db_conn):
    from db import add_restaurant
    add_restaurant(db_conn, "T123", "MyPlace", "Loc 1")
    
    respond = RespondStub()
    ack = MagicMock()
    # Pick for a different workspace
    body = {"team_id": "T999", "text": "pick"}
    
    handle_lunch_command(ack, body, respond, db_conn)
    assert "list is empty" in respond.calls[0]

def test_handle_lunch_invalid_subcommand(db_conn):
    respond = RespondStub()
    ack = MagicMock()
    body = {"team_id": "T123", "text": "jump"}
    
    handle_lunch_command(ack, body, respond, db_conn)
    assert "Unknown command" in respond.calls[0]