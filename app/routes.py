from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import URL
from app.auth import oauth2_scheme
router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/shorten/")
def shorten_url(long_url: str, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):

    # Generate a short URL (mock implementation)
    short_url = generate_unique_short_url(long_url)

    
    new_url = URL(short_url=short_url, long_url=long_url)
    db.add(new_url)
    db.commit()
    db.refresh(new_url)
    return new_url

@router.get("/{short_url}")
def redirect_url(short_url: str, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):

    url = db.query(URL).filter(URL.short_url == short_url).first()
    if not url:
        raise HTTPException(status_code=404, detail="URL not found")
    return {"long_url": url.long_url}
@router.get("/secure-data")
async def get_secure_data(token: str = Depends(oauth2_scheme)):
    """Protected route requiring OAuth authentication."""
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return {"message": "Secure data access granted!"}
