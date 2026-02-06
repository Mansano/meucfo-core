
import sys
import os
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from unittest.mock import MagicMock
import asyncio

# Add current directory to path
sys.path.insert(0, os.getcwd())

from app.main import app

async def test_render():
    print("Testing template rendering...")
    templates = Jinja2Templates(directory="app/templates")
    
    # Mock request
    scope = {
        "type": "http",
        "path": "/",
        "headers": [],
        "app": app,
    }
    request = Request(scope)
    
    try:
        response = templates.TemplateResponse(
            "dashboard.html",
            {"request": request, "title": "MeuCFO.ai - Dashboard", "current_user": None}
        )
        print("Rendering successful!")
        print(response.body[:100]) # Print first 100 chars
    except Exception as e:
        with open("render_error.log", "w") as f:
            f.write(f"Rendering failed: {e}\n")
            import traceback
            traceback.print_exc(file=f)

if __name__ == "__main__":
    asyncio.run(test_render())
