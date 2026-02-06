"""
Vercel Serverless Function Entry Point
This file is specifically for Vercel deployment
"""
import sys
import os

# Add server to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'server'))

# Import and expose the app
try:
    from main import app
    # Vercel looks for 'app' or 'handler'
    handler = app
except Exception as e:
    # Fallback error handler
    from fastapi import FastAPI
    app = FastAPI()
    handler = app
    
    @app.get("/")
    def error():
        return {"error": str(e), "message": "Failed to import main app"}
