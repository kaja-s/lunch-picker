import pytest
import os
import sqlite3
from db import init_db, add_restaurant, list_restaurants, remove_restaurant

@pytest.fixture(autouse=True)
def setup_db(monkeypatch):
    # Use in-memory DB for tests
    monkeypatch.setenv("DB_PATH", ":memory:")
    import db
    import importlib
    importlib.reload(db)
    db.init_db()

def test_add_and_list_restaurants():
    ws_id = "T123"
    add_restaurant(ws_id, "Pizza Place", "123 Street")
    results = list_restaurants(ws_id)
    assert len(results) == 1
    assert results[0]["name"] == "Pizza Place"

def test_duplicate_restaurant_error():
    ws_id = "T123"
    add_restaurant(ws_id, "Unique", "Loc")
    with pytest.raises(ValueError, match="already exists"):
        add_restaurant(ws_id, "Unique", "Other Loc")

def test_remove_restaurant():
    ws_id = "T123"
    add_restaurant(ws_id, "DeleteMe", "Nowhere")
    assert remove_restaurant(ws_id, "DeleteMe") is True
    assert len(list_restaurants(ws_id)) == 0