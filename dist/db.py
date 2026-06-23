import sqlite3
import os
import logging

# Configure logging for debugging purposes
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_db(db_path: str) -> sqlite3.Connection:
    """
    Initializes the SQLite database, creates necessary tables, and returns the connection.
    
    :param db_path: Path to the SQLite database file.
    :return: sqlite3.Connection object.
    :raises ConnectionError: If the database cannot be opened or initialized.
    """
    if not db_path:
        error_msg = "Database path must be a non-empty string."
        logger.error(error_msg)
        raise ValueError(error_msg)

    try:
        # Connect to the database
        # check_same_thread=False is used to support multi-threaded environments if needed,
        # especially important for in-memory testing configurations.
        conn = sqlite3.connect(db_path, check_same_thread=False)
        
        # Use Row factory for better accessibility in debugging and results
        conn.row_factory = sqlite3.Row
        
        cursor = conn.cursor()
        
        # Create the restaurants table
        # We use TEXT for workspace_id as Slack IDs are alphanumeric strings.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS restaurants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workspace_id TEXT NOT NULL,
                name TEXT NOT NULL,
                address TEXT NOT NULL
            )
        """)
        
        # Create an index on workspace_id for faster lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_restaurants_workspace 
            ON restaurants(workspace_id)
        """)
        
        conn.commit()
        logger.info(f"Database initialized successfully at: {db_path}")
        return conn

    except sqlite3.Error as e:
        error_info = f"SQLite error during initialization of '{db_path}': {e.args}"
        logger.error(error_info)
        raise ConnectionError(error_info) from e
    except Exception as e:
        error_info = f"Unexpected error during database initialization at '{db_path}': {str(e)}"
        logger.error(error_info)
        raise RuntimeError(error_info) from e

def add_restaurant(conn: sqlite3.Connection, workspace_id: str, name: str, address: str) -> None:
    """
    Adds a new restaurant to the database for a specific workspace.
    
    :param conn: The sqlite3 connection object.
    :param workspace_id: Slack workspace ID.
    :param name: Name of the restaurant.
    :param address: Physical address or URL.
    :raises ValueError: If a restaurant with the same name already exists in the workspace or inputs are invalid.
    """
    if not workspace_id or not name or not address:
        raise ValueError(f"workspace_id, name, and address must not be empty. Got: {workspace_id=}, {name=}, {address=}")

    try:
        cursor = conn.cursor()
        
        # Check for duplicates within the same workspace
        cursor.execute(
            "SELECT 1 FROM restaurants WHERE workspace_id = ? AND name = ?", 
            (workspace_id, name)
        )
        if cursor.fetchone():
            error_msg = f"Restaurant '{name}' already exists in workspace '{workspace_id}'."
            logger.warning(error_msg)
            raise ValueError(error_msg)
        
        cursor.execute(
            "INSERT INTO restaurants (workspace_id, name, address) VALUES (?, ?, ?)",
            (workspace_id, name, address)
        )
        conn.commit()
        logger.info(f"Added restaurant '{name}' to workspace '{workspace_id}'.")
        
    except sqlite3.Error as e:
        error_info = f"Database error while adding restaurant '{name}': {e}"
        logger.error(error_info)
        raise RuntimeError(error_info) from e

def remove_restaurant(conn: sqlite3.Connection, workspace_id: str, name: str) -> bool:
    """
    Removes a restaurant from the database for a specific workspace.
    
    :param conn: The sqlite3 connection object.
    :param workspace_id: Slack workspace ID.
    :param name: Name of the restaurant.
    :return: True if a restaurant was removed, False otherwise.
    :raises ValueError: If inputs are invalid.
    """
    if not workspace_id or not name:
        raise ValueError(f"workspace_id and name must not be empty. Got: {workspace_id=}, {name=}")

    try:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM restaurants WHERE workspace_id = ? AND name = ?",
            (workspace_id, name)
        )
        rows_deleted = cursor.rowcount
        conn.commit()
        
        if rows_deleted > 0:
            logger.info(f"Removed restaurant '{name}' from workspace '{workspace_id}'.")
            return True
        else:
            logger.info(f"No restaurant named '{name}' found in workspace '{workspace_id}' to remove.")
            return False

    except sqlite3.Error as e:
        error_info = (f"Database error while removing restaurant '{name}' "
                      f"from workspace '{workspace_id}': {e}")
        logger.error(error_info)
        raise RuntimeError(error_info) from e

def list_restaurants(conn: sqlite3.Connection, workspace_id: str) -> list[tuple[str, str]]:
    """
    Lists all restaurants for a specific workspace.
    
    :param conn: The sqlite3 connection object.
    :param workspace_id: Slack workspace ID.
    :return: A list of (name, address) tuples.
    :raises ValueError: If workspace_id is empty.
    """
    if not workspace_id:
        raise ValueError(f"workspace_id must not be empty. Got: {workspace_id=}")

    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name, address FROM restaurants WHERE workspace_id = ? ORDER BY name ASC",
            (workspace_id,)
        )
        rows = cursor.fetchall()
        
        # Convert sqlite3.Row or tuples to standard list of tuples
        results = [(row['name'], row['address']) for row in rows]
        logger.info(f"Retrieved {len(results)} restaurants for workspace '{workspace_id}'.")
        return results

    except sqlite3.Error as e:
        error_info = f"Database error while listing restaurants for workspace '{workspace_id}': {e}"
        logger.error(error_info)
        raise RuntimeError(error_info) from e

def pick_restaurant(conn: sqlite3.Connection, workspace_id: str) -> tuple[str, str] | None:
    """
    Randomly selects a restaurant for a specific workspace.
    
    :param conn: The sqlite3 connection object.
    :param workspace_id: Slack workspace ID.
    :return: A (name, address) tuple, or None if no restaurants are found.
    :raises ValueError: If workspace_id is empty.
    """
    if not workspace_id:
        raise ValueError(f"workspace_id must not be empty. Got: {workspace_id=}")

    try:
        cursor = conn.cursor()
        # Use SQL RANDOM() to pick one row efficiently
        cursor.execute(
            "SELECT name, address FROM restaurants WHERE workspace_id = ? ORDER BY RANDOM() LIMIT 1",
            (workspace_id,)
        )
        row = cursor.fetchone()
        
        if row:
            result = (row['name'], row['address'])
            logger.info(f"Picked restaurant '{result[0]}' for workspace '{workspace_id}'.")
            return result
        
        logger.info(f"No restaurants found to pick from for workspace '{workspace_id}'.")
        return None

    except sqlite3.Error as e:
        error_info = f"Database error while listing restaurants for workspace '{workspace_id}': {e}"
        logger.error(error_info)
        raise RuntimeError(error_info) from e