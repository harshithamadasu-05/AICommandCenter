import subprocess
import sys
import time
import os
import threading

def start_backend():
    print("Starting FastAPI Backend Server on http://127.0.0.1:8000 ...")
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.abspath(os.path.dirname(__file__))
    subprocess.run(
        [sys.executable, "-m", "uvicorn", "backend.app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=os.path.abspath(os.path.dirname(__file__)),
        env=env
    )

def start_frontend():
    print("Starting Streamlit Command Centre Dashboard on http://localhost:8501 ...")
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", "frontend/app.py"],
        cwd=os.path.abspath(os.path.dirname(__file__))
    )

if __name__ == "__main__":
    print("=" * 70)
    print("  AI-POWERED INTELLIGENT EMERGENCY HEALTHCARE COMMAND CENTRE  ")
    print("=" * 70)

    # Initialize DB first
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    from backend.app.db.seed_data import seed_database
    seed_database()

    # Launch Backend thread
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()

    time.sleep(2) # Give backend server time to boot

    # Launch Frontend
    start_frontend()
