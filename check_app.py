
import sys
import os
import faulthandler

# Enable faulthandler to get a traceback on segfaults
faulthandler.enable()

# Add current directory to path
sys.path.insert(0, os.getcwd())

print("Attempting to import app.main...")
try:
    from app.main import app
    print("Successfully imported app.main")
except Exception as e:
    print(f"Error importing app.main: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
