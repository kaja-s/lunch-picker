import sqlite3
import os
import logging
import random

logger = logging.getLogger(__name__)

def initialize_db(db_path: str = None) -> sqlite3.Connection:
    """
    Initializes the SQLite database. Creates the restaurants table if it doesn't exist.
    :param db_path: Path to the SQLite database file.
    :return: An open sqlite3.Connection object.
    """
    if db_path is None:
        db_path = os.environ.get("LUNCH_PICKER_DB", "lunch_picker.db")

    try:
        # check_same_thread=False is allowed for simple scripts, 
        # though standard sqlite3 usage is typically single-threaded.
        conn = sqlite3.connect(db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS restaurants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workspace_id TEXT NOT NULL,
                name TEXT NOT NULL,
                address TEXT NOT NULL
            )
        """)
        # Index for faster lookups by workspace
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_workspace ON restaurants(workspace_id)
        """)
        conn.commit()
        return conn
    except sqlite3.Error as e:
        logger.error(f"Failed to initialize database at {db_path}: {e}")
        raise

def add_restaurant(conn: sqlite3.Connection, workspace_id: str, name: str, address: str) -> None:
    """
    Adds a new restaurant to the workspace's list.
    Raises ValueError if the restaurant name already exists for the workspace.
    """
    try:
        cursor = conn.cursor()
        
        # Check for duplicates within the same workspace
        cursor.execute(
            "SELECT id FROM restaurants WHERE workspace_id = ? AND name = ? COLLATE NOCASE",
            (workspace_id, name)
        )
        if cursor.fetchone():
            raise ValueError(f"Restaurant '{name}' already exists in this workspace.")

        cursor.execute(
            "INSERT INTO restaurants (workspace_id, name, address) VALUES (?, ?, ?)",
            (workspace_id, name, address)
        )
        conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Database error while adding restaurant '{name}' for workspace {workspace_id}: {e}")
        raise

def remove_restaurant(conn: sqlite3.Connection, workspace_id: str, name: str) -> bool:
    """
    Removes a restaurant from the workspace's list.
    Returns True if a restaurant was removed, False otherwise.
    """
    try:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM restaurants WHERE workspace_id = ? AND name = ? COLLATE NOCASE",
            (workspace_id, name)
        )
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        logger.error(f"Database error while removing restaurant '{name}' for workspace {workspace_id}: {e}")
        raise

def list_restaurants(conn: sqlite3.Connection, workspace_id: str) -> list[tuple[str, str]]:
    """
    Returns all restaurants for the given workspace as a list of (name, address) pairs.
    """
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name, address FROM restaurants WHERE workspace_id = ? ORDER BY name ASC",
            (workspace_id,)
        )
        rows = cursor.fetchall()
        return [(row["name"], row["address"]) for row in rows]
    except sqlite3.Error as e:
        logger.error(f"Database error while listing restaurants for workspace {workspace_id}: {e}")
        raise

def pick_restaurant(conn: sqlite3.Connection, workspace_id: str) -> tuple[str, str] | None:
    """
    Returns a randomly selected (name, address) pair from the workspace's list.
    Returns None if the list is empty.
    """
    try:
        restaurants = list_restaurants(conn, workspace_id)
        if not restaurants:
            return None
        
        return random.choice(restaurants)
    except Exception as e:
        logger.error(f"Error while picking restaurant for workspace {workspace_id}: {e}")
        raise