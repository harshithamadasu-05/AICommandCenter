import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "emergency_command_centre.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

API_HOST = "127.0.0.1"
API_PORT = 8000
