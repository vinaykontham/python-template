from fastapi import APIRouter
from app.auth import router as auth_router

router = APIRouter()

@router.get("/")
def read_root():
    return {"message": "FastAPI Template Ready"}

router.include_router(auth_router)