from fastapi import APIRouter
from app.auth import router as auth_router
import os
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/urls")

router = APIRouter()

@router.get("/")
def read_root():
    return {"message": "FastAPI Template Ready"}

router.include_router(auth_router)