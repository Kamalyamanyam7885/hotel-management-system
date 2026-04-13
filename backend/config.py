"""
Configuration for Hotel Management System.
All values read from environment variables — no hardcoded secrets.
"""
import os
from dotenv import load_dotenv

# Load .env file if present (local development)
load_dotenv()

DB_CONFIG = {
    "host": os.environ.get("MYSQL_HOST", "localhost"),
    "user": os.environ.get("MYSQL_USER", "root"),
    "password": os.environ.get("MYSQL_PASSWORD", ""),
    "database": os.environ.get("MYSQL_DB", "hotel_management"),
}

SECRET_KEY = os.environ.get("JWT_SECRET", "change-me-in-production")