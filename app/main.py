from fastapi import FastAPI
from app.routes import router
from app.database import engine, Base

# Initialize FastAPI app
app = FastAPI(title="FastAPI URL Shortener")

# Create database tables
Base.metadata.create_all(bind=engine)

# Include API routes
app.include_router(router)

@app.get("/")
def read_root():
    return {"message": "FastAPI Template Ready"}
