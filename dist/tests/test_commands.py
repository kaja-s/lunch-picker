import pytest
from unittest.mock import MagicMock
from commands import handle_lunch_command

@pytest.fixture
def mock_say():
    return MagicMock()

@pytest.fixture
def mock_ack():
    return MagicMock()

def test_handle_lunch_add(monkeypatch, mock_ack, mock_say):
    # Mock DB to avoid file I/O
    monkeypatch.setenv("DB_PATH", ":memory:")
    import db
    import importlib
    importlib.reload(db)
    db.init_db()
    
    body = {
        "text": "add BurgerKing HighStreet",
        "team_id": "T001"
    }
    
    handle_lunch_command(mock_ack, body, mock_say)
    
    mock_ack.assert_called_once()
    mock_say.assert_called_with("Added *BurgerKing* (HighStreet) to the lunch list.")

def test_handle_lunch_add_missing_args(monkeypatch, mock_ack, mock_say):
    monkeypatch.setenv("DB_PATH", ":memory:")
    import db
    import importlib
    importlib.reload(db)
    db.init_db()
    
    body = {
        "text": "add OnlyName",
        "team_id": "T001"
    }
    
    handle_lunch_command(mock_ack, body, mock_say)
    mock_say.assert_called_with("Usage: /lunch add <name> <address>")

def test_handle_lunch_add_duplicate(monkeypatch, mock_ack, mock_say):
    monkeypatch.setenv("DB_PATH", ":memory:")
    import db
    import importlib
    importlib.reload(db)
    db.init_db()
    
    body = {
        "text": "add Pizza Street1",
        "team_id": "T001"
    }
    
    # First add
    handle_lunch_command(mock_ack, body, mock_say)
    # Second add (duplicate)
    handle_lunch_command(mock_ack, body, mock_say)
    
    mock_say.assert_called_with("An error occurred: Restaurant 'Pizza' already exists in this workspace.")

def test_handle_lunch_remove_success(monkeypatch, mock_ack, mock_say):
    monkeypatch.setenv("DB_PATH", ":memory:")
    import db
    import importlib
    importlib.reload(db)
    db.init_db()
    
    # Setup
    db.add_restaurant("T001", "Subway", "Downstairs")
    
    body = {
        "text": "remove Subway",
        "team_id": "T001"
    }
    
    handle_lunch_command(mock_ack, body, mock_say)
    mock_say.assert_called_with("Removed *Subway* from the lunch list.")

def test_handle_lunch_remove_missing_args(mock_ack, mock_say):
    body = {
        "text": "remove",
        "team_id": "T001"
    }
    handle_lunch_command(mock_ack, body, mock_say)
    mock_say.assert_called_with("Usage: /lunch remove <name>")

def test_handle_lunch_remove_not_found(monkeypatch, mock_ack, mock_say):
    monkeypatch.setenv("DB_PATH", ":memory:")
    import db
    import importlib
    importlib.reload(db)
    db.init_db()
    
    body = {
        "text": "remove NonExistent",
        "team_id": "T001"
    }
    handle_lunch_command(mock_ack, body, mock_say)
    mock_say.assert_called_with("Restaurant *NonExistent* not found in the lunch list.")

def test_handle_lunch_pick_empty(monkeypatch, mock_ack, mock_say):
    monkeypatch.setenv("DB_PATH", ":memory:")
    import db
    import importlib
    importlib.reload(db)
    db.init_db()
    
    body = {"text": "pick", "team_id": "T999"}
    handle_lunch_command(mock_ack, body, mock_say)
    
    mock_say.assert_called_with("No restaurants have been added yet.")

def test_handle_lunch_pick_success(monkeypatch, mock_ack, mock_say):
    monkeypatch.setenv("DB_PATH", ":memory:")
    import db
    import importlib
    importlib.reload(db)
    db.init_db()
    
    ws_id = "T_PICK"
    db.add_restaurant(ws_id, "Target", "Address A")
    
    body = {"text": "pick", "team_id": ws_id}
    handle_lunch_command(mock_ack, body, mock_say)
    
    mock_say.assert_called_with("Today's lunch spot: *Target* (Address A)")

def test_handle_lunch_list_empty(monkeypatch, mock_ack, mock_say):
    monkeypatch.setenv("DB_PATH", ":memory:")
    import db
    import importlib
    importlib.reload(db)
    db.init_db()
    
    body = {"text": "list", "team_id": "T111"}
    handle_lunch_command(mock_ack, body, mock_say)
    mock_say.assert_called_with("No restaurants have been added yet.")

def test_handle_lunch_list_success(monkeypatch, mock_ack, mock_say):
    monkeypatch.setenv("DB_PATH", ":memory:")
    import db
    import importlib
    importlib.reload(db)
    db.init_db()
    
    ws_id = "T111"
    db.add_restaurant(ws_id, "Cafe A", "Street A")
    db.add_restaurant(ws_id, "Bistro B", "Street B")
    
    body = {"text": "list", "team_id": ws_id}
    handle_lunch_command(mock_ack, body, mock_say)
    
    expected_output = "Here are the restaurants:\n• *Bistro B* - Street B\n• *Cafe A* - Street A"
    mock_say.assert_called_with(expected_output)