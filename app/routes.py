from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import URL

router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/shorten/")
def shorten_url(long_url: str, db: Session = Depends(get_db)):
    # Generate a short URL (mock implementation)
    short_url = long_url[:6]
    
    new_url = URL(short_url=short_url, long_url=long_url)
    db.add(new_url)
    db.commit()
    db.refresh(new_url)
    return new_url

@router.get("/{short_url}")
def redirect_url(short_url: str, db: Session = Depends(get_db)):
    url = db.query(URL).filter(URL.short_url == short_url).first()
    if not url:
        raise HTTPException(status_code=404, detail="URL not found")
    return {"long_url": url.long_url}
