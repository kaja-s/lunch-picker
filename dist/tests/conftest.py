import sys
import os

# Set dummy environment variables before importing the app
os.environ["SLACK_BOT_TOKEN"] = "xoxb-test-token"
os.environ["SLACK_SIGNING_SECRET"] = "test-signing-secret"
os.environ["LUNCH_PICKER_DB"] = ":memory:"

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))