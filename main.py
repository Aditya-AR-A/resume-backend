"""
Main entry point for the Resume Backend API
This file imports and runs the FastAPI application from the app package
"""

from app.main import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
