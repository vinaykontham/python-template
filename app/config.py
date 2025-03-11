import os
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()
IS_TEST_ENV = os.getenv("PYTHON_ENV") == "test"

DATABASE_URL = "sqlite:///./test.db" if IS_TEST_ENV else os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/urls")

OAUTH_CLIENT_ID = os.getenv("OAUTH_CLIENT_ID")
OAUTH_CLIENT_SECRET = os.getenv("OAUTH_CLIENT_SECRET")
OAUTH_REDIRECT_URI = os.getenv("OAUTH_REDIRECT_URI", "http://localhost:8000/auth/callback")
OAUTH_PROVIDER_URL = "https://accounts.google.com" if IS_TEST_ENV else os.getenv("OAUTH_PROVIDER_URL", "https://accounts.google.com")