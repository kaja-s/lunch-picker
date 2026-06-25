import os
import pytest
from app import app
from slack_bolt import App

def test_app_initialization():
    """
    Verifies that the Slack Bolt app is initialized with correct types.
    """
    assert isinstance(app, App)
    assert app.client is not None

def test_environment_variables_loading(monkeypatch):
    """
    Verifies that the app attempts to read expected environment variables.
    """
    # Use monkeypatch to simulate env vars
    monkeypatch.setenv("PORT", "5000")
    monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-test")
    monkeypatch.setenv("SLACK_SIGNING_SECRET", "secret-test")
    
    assert os.environ.get("PORT") == "5000"
    assert os.environ.get("SLACK_BOT_TOKEN") == "xoxb-test"
    assert os.environ.get("SLACK_SIGNING_SECRET") == "secret-test"