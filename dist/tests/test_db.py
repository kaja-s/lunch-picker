import pytest
import sqlite3
import os
from db import initialize_db, add_restaurant, remove_restaurant, list_restaurants, pick_restaurant

def test_initialize_db_in_memory():
    """Verify that the database can be initialized in memory and tables are created."""
    conn = initialize_db(":memory:")
    assert isinstance(conn, sqlite3.Connection)
    
    # Check if table exists
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='restaurants';")
    table = cursor.fetchone()
    assert table is not None
    assert table['name'] == 'restaurants'
    conn.close()

def test_initialize_db_schema():
    """Verify that the schema has the required columns."""
    conn = initialize_db(":memory:")
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(restaurants);")
    columns = {row['name']: row['type'] for row in cursor.fetchall()}
    
    assert "workspace_id" in columns
    assert "name" in columns
    assert "address" in columns
    conn.close()

def test_initialize_db_invalid_path():
    """Verify that an empty path raises a ValueError."""
    with pytest.raises(ValueError) as excinfo:
        initialize_db("")
    assert "Database path must be a non-empty string" in str(excinfo.value)

def test_initialize_db_persistence(tmp_path):
    """Verify that the database file is actually created on disk."""
    db_file = tmp_path / "test_lunch.db"
    db_path = str(db_file)
    
    conn = initialize_db(db_path)
    conn.close()
    
    assert os.path.exists(db_path)
    assert os.path.getsize(db_path) > 0

def test_add_restaurant_success():
    """Verify that a restaurant can be successfully added."""
    conn = initialize_db(":memory:")
    add_restaurant(conn, "W123", "Burger Queen", "123 Flame St")
    
    cursor = conn.cursor()
    cursor.execute("SELECT workspace_id, name, address FROM restaurants WHERE name='Burger Queen'")
    row = cursor.fetchone()
    assert row is not None
    assert row['workspace_id'] == "W123"
    assert row['address'] == "123 Flame St"
    conn.close()

def test_add_restaurant_duplicate_error():
    """Verify that adding a duplicate restaurant name in the same workspace raises ValueError."""
    conn = initialize_db(":memory:")
    add_restaurant(conn, "W123", "Taco Hut", "456 Shell Rd")
    
    with pytest.raises(ValueError) as excinfo:
        add_restaurant(conn, "W123", "Taco Hut", "789 New Rd")
    assert "already exists in workspace 'W123'" in str(excinfo.value)
    conn.close()

def test_add_restaurant_same_name_different_workspaces():
    """Verify that restaurants with the same name can exist in different workspaces."""
    conn = initialize_db(":memory:")
    add_restaurant(conn, "W123", "Pizza Place", "Addr 1")
    # This should not raise an error
    add_restaurant(conn, "W999", "Pizza Place", "Addr 2")
    
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM restaurants WHERE name='Pizza Place'")
    assert cursor.fetchone()['count'] == 2
    conn.close()

def test_add_restaurant_invalid_input():
    """Verify that empty inputs raise ValueError."""
    conn = initialize_db(":memory:")
    with pytest.raises(ValueError):
        add_restaurant(conn, "", "Name", "Addr")
    with pytest.raises(ValueError):
        add_restaurant(conn, "W1", "", "Addr")
    with pytest.raises(ValueError):
        add_restaurant(conn, "W1", "Name", "")
    conn.close()

def test_remove_restaurant_success():
    """Verify that a restaurant can be successfully removed."""
    conn = initialize_db(":memory:")
    add_restaurant(conn, "W123", "Burger Queen", "123 Flame St")
    
    deleted = remove_restaurant(conn, "W123", "Burger Queen")
    assert deleted is True
    
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM restaurants WHERE name='Burger Queen'")
    assert cursor.fetchone() is None
    conn.close()

def test_remove_restaurant_not_found():
    """Verify that removing a non-existent restaurant returns False."""
    conn = initialize_db(":memory:")
    deleted = remove_restaurant(conn, "W123", "Non Existent")
    assert deleted is False
    conn.close()

def test_remove_restaurant_workspace_isolation():
    """Verify that removing a restaurant in one workspace does not affect another."""
    conn = initialize_db(":memory:")
    add_restaurant(conn, "W1", "Target", "Addr 1")
    add_restaurant(conn, "W2", "Target", "Addr 2")
    
    deleted = remove_restaurant(conn, "W1", "Target")
    assert deleted is True
    
    cursor = conn.cursor()
    cursor.execute("SELECT workspace_id FROM restaurants WHERE name='Target'")
    remaining = cursor.fetchall()
    assert len(remaining) == 1
    assert remaining[0]['workspace_id'] == "W2"
    conn.close()

def test_remove_restaurant_invalid_input():
    """Verify that empty inputs for removal raise ValueError."""
    conn = initialize_db(":memory:")
    with pytest.raises(ValueError):
        remove_restaurant(conn, "", "Name")
    with pytest.raises(ValueError):
        remove_restaurant(conn, "W1", "")
    conn.close()

def test_list_restaurants_success():
    """Verify that restaurants are listed correctly for a workspace."""
    conn = initialize_db(":memory:")
    add_restaurant(conn, "W1", "Bistro A", "Addr A")
    add_restaurant(conn, "W1", "Cafe B", "Addr B")
    
    restaurants = list_restaurants(conn, "W1")
    assert len(restaurants) == 2
    assert ("Bistro A", "Addr A") in restaurants
    assert ("Cafe B", "Addr B") in restaurants
    conn.close()

def test_list_restaurants_empty():
    """Verify that an empty list is returned if no restaurants exist."""
    conn = initialize_db(":memory:")
    restaurants = list_restaurants(conn, "W-EMPTY")
    assert restaurants == []
    conn.close()

def test_list_restaurants_isolation():
    """Verify that listing is isolated to the specific workspace."""
    conn = initialize_db(":memory:")
    add_restaurant(conn, "W1", "Common Name", "Addr 1")
    add_restaurant(conn, "W2", "Other Place", "Addr 2")
    
    w1_list = list_restaurants(conn, "W1")
    assert len(w1_list) == 1
    assert w1_list[0][0] == "Common Name"
    conn.close()

def test_list_restaurants_invalid_input():
    """Verify that empty workspace_id raises ValueError."""
    conn = initialize_db(":memory:")
    with pytest.raises(ValueError):
        list_restaurants(conn, "")
    conn.close()

def test_pick_restaurant_success():
    """Verify that a restaurant is picked when the list is not empty."""
    conn = initialize_db(":memory:")
    add_restaurant(conn, "W1", "Target 1", "Addr 1")
    add_restaurant(conn, "W1", "Target 2", "Addr 2")
    
    picked = pick_restaurant(conn, "W1")
    assert picked is not None
    assert picked[0] in ["Target 1", "Target 2"]
    assert picked[1] in ["Addr 1", "Addr 2"]
    conn.close()

def test_pick_restaurant_empty():
    """Verify that picking from an empty workspace returns None."""
    conn = initialize_db(":memory:")
    picked = pick_restaurant(conn, "W-EMPTY")
    assert picked is None
    conn.close()

def test_pick_restaurant_invalid_input():
    """Verify that empty workspace_id for picking raises ValueError."""
    conn = initialize_db(":memory:")
    with pytest.raises(ValueError):
        pick_restaurant(conn, "")
    conn.close()