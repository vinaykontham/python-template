from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import hashlib

app = FastAPI()

class ShortenRequest(BaseModel):
    long_url: str  # Ensure this matches the test request payload

url_db = {}

@app.get("/")
def root():
    return {"message": "FastAPI Template Ready"}

@app.post("/shorten/")
def shorten_url(request: ShortenRequest):
    if not request.long_url:
        raise HTTPException(status_code=400, detail="long_url is required")
    
    short_hash = hashlib.md5(request.long_url.encode()).hexdigest()[:6]
    url_db[short_hash] = request.long_url
    return {"short_url": short_hash}

@app.get("/{short_url}")
def redirect_url(short_url: str):
    if short_url not in url_db:
        raise HTTPException(status_code=404, detail="URL not found")
    return {"long_url": url_db[short_url]}
