import sqlite3
import os

_connection = None

def get_connection():
    global _connection
    db_path = os.environ.get("DB_PATH", "lunch_picker.db")
    
    if _connection is None:
        # check_same_thread=False is needed for some environments/tests
        _connection = sqlite3.connect(db_path, check_same_thread=False)
        _connection.row_factory = sqlite3.Row
    return _connection

def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS restaurants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workspace_id TEXT NOT NULL,
            name TEXT NOT NULL,
            address TEXT NOT NULL,
            UNIQUE(workspace_id, name)
        )
    """)
    conn.commit()

def add_restaurant(workspace_id, name, address):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO restaurants (workspace_id, name, address) VALUES (?, ?, ?)",
            (workspace_id, name, address)
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        raise ValueError(f"Restaurant '{name}' already exists in this workspace.") from e

def list_restaurants(workspace_id):
    conn = get_connection()
    cursor = conn.execute(
        "SELECT name, address FROM restaurants WHERE workspace_id = ? ORDER BY name ASC",
        (workspace_id,)
    )
    return [dict(row) for row in cursor.fetchall()]

def remove_restaurant(workspace_id, name):
    conn = get_connection()
    cursor = conn.execute(
        "DELETE FROM restaurants WHERE workspace_id = ? AND name = ?",
        (workspace_id, name)
    )
    conn.commit()
    return cursor.rowcount > 0