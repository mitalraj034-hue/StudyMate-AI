import sys
from pathlib import Path

# Ensure backend directory is in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Re-export app from the modular app package
from app.main import app

if __name__ == "__main__":
    import uvicorn
    module_target = "backend.main:app" if Path.cwd().name != "backend" else "app.main:app"
    uvicorn.run(module_target, host="127.0.0.1", port=8000, reload=True)
