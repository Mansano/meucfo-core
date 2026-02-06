
import sys
import os
from fastapi import FastAPI
from starlette.routing import Mount

# Add current directory to path
sys.path.insert(0, os.getcwd())

from app.main import app

print("Listing all routes:")
for route in app.routes:
    if isinstance(route, Mount):
        print(f"Mount: {route.path} -> {route.name}")
    else:
        print(f"Route: {route.path} -> {route.name}")

print("\nTesting url_for('dashboard'):")
try:
    url = app.url_path_for("dashboard")
    print(f"Success: 'dashboard' resolves to {url}")
except Exception as e:
    print(f"Error: {e}")

print("\nTesting url_for('static', path='css/style.css'):")
try:
    url = app.url_path_for("static", path="css/style.css")
    print(f"Success: 'static' resolves to {url}")
except Exception as e:
    print(f"Error: {e}")
