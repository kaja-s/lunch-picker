import sys
import os

# Ensure the root directory is in sys.path so that 'db' and 'commands' can be imported.
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))