import uvicorn
import sys
import os

sys.path.append(os.getcwd())

if __name__ == "__main__":
    try:
        from backend.main import app
        print("Import successful!")
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
    except Exception as e:
        import traceback
        print("CRASHED AT STARTUP OR IMPORT:")
        traceback.print_exc()
