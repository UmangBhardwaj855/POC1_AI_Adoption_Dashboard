import sys
import os

# Add the server directory to the Python path
server_path = os.path.join(os.path.dirname(__file__), '..', 'server')
sys.path.insert(0, os.path.abspath(server_path))

# Import the FastAPI app
from main import app

# Vercel expects either 'app' or 'handler'
handler = app
