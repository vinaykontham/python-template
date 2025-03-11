import os
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()
IS_TEST_ENV = os.getenv("PYTHON_ENV") == "test"

DATABASE_URL = "sqlite:///./test.db" if IS_TEST_ENV else os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/urls")