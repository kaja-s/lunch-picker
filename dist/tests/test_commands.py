import pytest
from unittest.mock import MagicMock, patch
from commands import handle_lunch_command

def test_handle_lunch_add_success():
    ack = MagicMock()
    respond = MagicMock()
    conn = MagicMock()
    body = {
        "text": "add PizzaPlace http://maps.google.com",
        "user_id": "U123",
        "team_id": "T123"
    }

    with patch("db.add_restaurant") as mock_add:
        handle_lunch_command(ack, body, respond, conn)
        
        ack.assert_called_once()
        mock_add.assert_called_once_with(conn, "T123", "PizzaPlace", "http://maps.google.com")
        respond.assert_called_once()
        assert "Added restaurant: *PizzaPlace*" in respond.call_args[0][0]

def test_handle_lunch_add_missing_args():
    ack = MagicMock()
    respond = MagicMock()
    conn = MagicMock()
    body = {
        "text": "add OnlyName",
        "user_id": "U123",
        "team_id": "T123"
    }

    handle_lunch_command(ack, body, respond, conn)
    
    respond.assert_called_once_with("Usage: /lunch add <name> <address>")

def test_handle_lunch_add_duplicate():
    ack = MagicMock()
    respond = MagicMock()
    conn = MagicMock()
    body = {
        "text": "add PizzaPlace http://maps.google.com",
        "user_id": "U123",
        "team_id": "T123"
    }

    with patch("db.add_restaurant") as mock_add:
        mock_add.side_effect = ValueError("Restaurant 'PizzaPlace' already exists in workspace 'T123'.")
        
        handle_lunch_command(ack, body, respond, conn)
        
        respond.assert_called_once()
        assert "already exists" in respond.call_args[0][0]

def test_handle_lunch_remove_success():
    ack = MagicMock()
    respond = MagicMock()
    conn = MagicMock()
    body = {
        "text": "remove PizzaPlace",
        "user_id": "U123",
        "team_id": "T123"
    }

    with patch("db.remove_restaurant") as mock_remove:
        mock_remove.return_value = True
        handle_lunch_command(ack, body, respond, conn)
        
        ack.assert_called_once()
        mock_remove.assert_called_once_with(conn, "T123", "PizzaPlace")
        respond.assert_called_once_with("Removed restaurant: *PizzaPlace*")

def test_handle_lunch_remove_missing_args():
    ack = MagicMock()
    respond = MagicMock()
    conn = MagicMock()
    body = {
        "text": "remove ",
        "user_id": "U123",
        "team_id": "T123"
    }

    handle_lunch_command(ack, body, respond, conn)
    respond.assert_called_once_with("Usage: /lunch remove <name>")

def test_handle_lunch_remove_not_found():
    ack = MagicMock()
    respond = MagicMock()
    conn = MagicMock()
    body = {
        "text": "remove GhostKitchen",
        "user_id": "U123",
        "team_id": "T123"
    }

    with patch("db.remove_restaurant") as mock_remove:
        mock_remove.return_value = False
        handle_lunch_command(ack, body, respond, conn)
        
        respond.assert_called_once_with("Error: Restaurant 'GhostKitchen' was not found.")

def test_handle_lunch_list_success():
    ack = MagicMock()
    respond = MagicMock()
    conn = MagicMock()
    body = {
        "text": "list",
        "user_id": "U123",
        "team_id": "T123"
    }

    with patch("db.list_restaurants") as mock_list:
        mock_list.return_value = [("Pizza Place", "123 Street"), ("Burger Joint", "456 Avenue")]
        handle_lunch_command(ack, body, respond, conn)
        
        ack.assert_called_once()
        respond.assert_called_once()
        response_text = respond.call_args[0][0]
        assert "Pizza Place" in response_text
        assert "123 Street" in response_text
        assert "Burger Joint" in response_text

def test_handle_lunch_list_empty():
    ack = MagicMock()
    respond = MagicMock()
    conn = MagicMock()
    body = {
        "text": "list",
        "user_id": "U123",
        "team_id": "T123"
    }

    with patch("db.list_restaurants") as mock_list:
        mock_list.return_value = []
        handle_lunch_command(ack, body, respond, conn)
        
        respond.assert_called_once_with("No restaurants have been added yet.")

def test_handle_lunch_pick_success():
    ack = MagicMock()
    respond = MagicMock()
    conn = MagicMock()
    body = {
        "text": "pick",
        "user_id": "U123",
        "team_id": "T123"
    }

    with patch("db.pick_restaurant") as mock_pick:
        mock_pick.return_value = ("Lucky Sushi", "789 Fish Lane")
        handle_lunch_command(ack, body, respond, conn)
        
        ack.assert_called_once()
        mock_pick.assert_called_once_with(conn, "T123")
        respond.assert_called_once_with("How about *Lucky Sushi*?\nAddress: 789 Fish Lane")

def test_handle_lunch_pick_empty():
    ack = MagicMock()
    respond = MagicMock()
    conn = MagicMock()
    body = {
        "text": "pick",
        "user_id": "U123",
        "team_id": "T123"
    }

    with patch("db.pick_restaurant") as mock_pick:
        mock_pick.return_value = None
        handle_lunch_command(ack, body, respond, conn)
        
        respond.assert_called_once_with("No restaurants have been added yet.")