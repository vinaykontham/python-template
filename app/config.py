from fastapi import APIRouter
from app.auth import router as auth_router
import os
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()
IS_TEST_ENV = os.getenv("PYTHON_ENV") == "test"

DATABASE_URL = "sqlite:///./test.db" if IS_TEST_ENV else os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/urls")

router = APIRouter()

@router.get("/")
def read_root():
    return {"message": "FastAPI Template Ready"}

router.include_router(auth_router)