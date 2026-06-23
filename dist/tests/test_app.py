import pytest
import os
from unittest.mock import MagicMock, patch
from app import create_app

def test_create_app_missing_env_vars():
    """Test that app raises error if required environment variables are missing."""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(EnvironmentError) as excinfo:
            create_app()
        assert "SLACK_BOT_TOKEN" in str(excinfo.value)

@patch("app.initialize_db")
@patch("app.App")
def test_create_app_success(mock_bolt_app, mock_init_db):
    """Test successful initialization of the app."""
    env_vars = {
        "SLACK_BOT_TOKEN": "xoxb-test",
        "SLACK_SIGNING_SECRET": "secret-test",
        "DATABASE_PATH": ":memory:"
    }
    
    with patch.dict(os.environ, env_vars):
        app = create_app()
        
        # Verify DB initialization was called
        mock_init_db.assert_called_once_with(":memory:")
        
        # Verify Bolt App was initialized with correct credentials
        mock_bolt_app.assert_called_once_with(
            token="xoxb-test",
            signing_secret="secret-test"
        )

def test_handle_lunch_command_routing():
    """Test that the command handler calls respond with expected stub message."""
    from commands import handle_lunch_command
    
    # Mock objects
    ack = MagicMock()
    respond = MagicMock()
    conn = MagicMock()
    body = {
        "text": "ping",
        "user_id": "U123",
        "team_id": "T123"
    }
    
    handle_lunch_command(ack, body, respond, conn)
    
    # Check that Slack's requirement to ack within 3s is met
    ack.assert_called_once()
    
    # Check that respond was called (verifying logic flow)
    respond.assert_called_once()
    args, _ = respond.call_args
    assert "ping" in args[0]