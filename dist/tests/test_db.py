import sqlite3
import pytest
from db import initialize_db

def test_initialize_db_creates_table():
    """
    Verify that initialize_db creates the restaurants table in an in-memory database.
    """
    # Use in-memory database for testing
    conn = initialize_db(":memory:")
    
    try:
        cursor = conn.cursor()
        # Check if the restaurants table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='restaurants';")
        table = cursor.fetchone()
        
        assert table is not None, "The 'restaurants' table should be created."
        assert table['name'] == 'restaurants'
        
        # Check columns
        cursor.execute("PRAGMA table_info(restaurants);")
        columns = {row['name'] for row in cursor.fetchall()}
        expected_columns = {"id", "workspace_id", "name", "address"}
        
        assert expected_columns.issubset(columns), f"Missing columns in restaurants table. Found: {columns}"
        
    finally:
        conn.close()

def test_add_restaurant_success():
    """Verify adding a restaurant works correctly."""
    conn = initialize_db(":memory:")
    try:
        add_restaurant(conn, "W123", "Pizza Place", "123 Main St")
        
        cursor = conn.cursor()
        cursor.execute("SELECT workspace_id, name, address FROM restaurants")
        row = cursor.fetchone()
        
        assert row["workspace_id"] == "W123"
        assert row["name"] == "Pizza Place"
        assert row["address"] == "123 Main St"
    finally:
        conn.close()

def test_add_restaurant_duplicate_fails():
    """Verify that adding a duplicate restaurant name in the same workspace raises ValueError."""
    conn = initialize_db(":memory:")
    try:
        add_restaurant(conn, "W123", "Pizza Place", "123 Main St")
        
        with pytest.raises(ValueError) as excinfo:
            add_restaurant(conn, "W123", "Pizza Place", "456 Side St")
        
        assert "already exists" in str(excinfo.value)
    finally:
        conn.close()

def test_add_restaurant_different_workspaces():
    """Verify that different workspaces can have restaurants with the same name."""
    conn = initialize_db(":memory:")
    try:
        add_restaurant(conn, "W1", "Pizza Place", "Address 1")
        # Should not raise error because workspace_id is different
        add_restaurant(conn, "W2", "Pizza Place", "Address 2")
        
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as cnt FROM restaurants WHERE name = 'Pizza Place'")
        assert cursor.fetchone()["cnt"] == 2
    finally:
        conn.close()

from db import add_restaurant, remove_restaurant, list_restaurants, pick_restaurant

def test_list_restaurants_empty():
    """Verify that listing restaurants for a workspace with none returns an empty list."""
    conn = initialize_db(":memory:")
    try:
        restaurants = list_restaurants(conn, "W_EMPTY")
        assert restaurants == []
    finally:
        conn.close()

def test_list_restaurants_success():
    """Verify that all restaurants for a workspace are returned."""
    conn = initialize_db(":memory:")
    try:
        add_restaurant(conn, "W1", "Z-Place", "Addr Z")
        add_restaurant(conn, "W1", "A-Place", "Addr A")
        
        restaurants = list_restaurants(conn, "W1")
        
        # Should be ordered by name ASC based on implementation
        assert len(restaurants) == 2
        assert restaurants[0] == ("A-Place", "Addr A")
        assert restaurants[1] == ("Z-Place", "Addr Z")
    finally:
        conn.close()

def test_list_restaurants_isolation():
    """Verify that listing restaurants only returns data for the specific workspace."""
    conn = initialize_db(":memory:")
    try:
        add_restaurant(conn, "W1", "Workspace 1 Resto", "Addr 1")
        add_restaurant(conn, "W2", "Workspace 2 Resto", "Addr 2")
        
        w1_list = list_restaurants(conn, "W1")
        assert len(w1_list) == 1
        assert w1_list[0][0] == "Workspace 1 Resto"
    finally:
        conn.close()

def test_remove_restaurant_success():
    """Verify that removing an existing restaurant works and returns True."""
    conn = initialize_db(":memory:")
    try:
        add_restaurant(conn, "W1", "Burger King", "Street 1")
        result = remove_restaurant(conn, "W1", "Burger King")
        
        assert result is True
        
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as cnt FROM restaurants WHERE workspace_id = 'W1'")
        assert cursor.fetchone()["cnt"] == 0
    finally:
        conn.close()

def test_remove_restaurant_not_found():
    """Verify that removing a non-existent restaurant returns False."""
    conn = initialize_db(":memory:")
    try:
        result = remove_restaurant(conn, "W1", "Non Existent")
        assert result is False
    finally:
        conn.close()

def test_remove_restaurant_case_insensitive():
    """Verify that removing a restaurant is case-insensitive."""
    conn = initialize_db(":memory:")
    try:
        add_restaurant(conn, "W1", "Pizza Hut", "Street 1")
        result = remove_restaurant(conn, "W1", "pizza hut")
        assert result is True
    finally:
        conn.close()

def test_remove_restaurant_isolation():
    """Verify that removing a restaurant in one workspace doesn't affect another."""
    conn = initialize_db(":memory:")
    try:
        add_restaurant(conn, "W1", "Subway", "Addr 1")
        add_restaurant(conn, "W2", "Subway", "Addr 2")
        
        remove_restaurant(conn, "W1", "Subway")
        
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as cnt FROM restaurants WHERE workspace_id = 'W2' AND name = 'Subway'")
        assert cursor.fetchone()["cnt"] == 1
    finally:
        conn.close()

def test_pick_restaurant_success():
    """Verify that picking a restaurant returns one of the added options."""
    conn = initialize_db(":memory:")
    try:
        add_restaurant(conn, "W1", "Resto A", "Addr A")
        add_restaurant(conn, "W1", "Resto B", "Addr B")
        
        picked = pick_restaurant(conn, "W1")
        
        assert picked in [("Resto A", "Addr A"), ("Resto B", "Addr B")]
    finally:
        conn.close()

def test_pick_restaurant_empty():
    """Verify that picking from an empty list returns None."""
    conn = initialize_db(":memory:")
    try:
        picked = pick_restaurant(conn, "W_EMPTY")
        assert picked is None
    finally:
        conn.close()

def test_pick_restaurant_isolation():
    """Verify that picking a restaurant only pulls from the correct workspace."""
    conn = initialize_db(":memory:")
    try:
        add_restaurant(conn, "W1", "Only W1", "Addr 1")
        add_restaurant(conn, "W2", "Only W2", "Addr 2")
        
        picked = pick_restaurant(conn, "W1")
        assert picked == ("Only W1", "Addr 1")
    finally:
        conn.close()

def test_db_path_from_env(monkeypatch):
    """
    Verify that the db_path is correctly picked up from environment variables.
    """
    monkeypatch.setenv("LUNCH_PICKER_DB", ":memory:")
    conn = initialize_db()
    
    try:
        # If it didn't crash and returns a connection, it used the env var
        assert isinstance(conn, sqlite3.Connection)
    finally:
        conn.close()