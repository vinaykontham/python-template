import logging
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import hashlib

logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for detailed logs
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Serve HTML templates
templates = Jinja2Templates(directory="app/templates")

class ShortenRequest(BaseModel):
    long_url: str

url_db = {}

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/shorten/")
def shorten_url(request: ShortenRequest):
    short_hash = hashlib.md5(request.long_url.encode()).hexdigest()[:6]
    url_db[short_hash] = request.long_url
    return {"short_url": short_hash}

@app.get("/{short_url}")
def redirect_url(short_url: str):
    if short_url not in url_db:
        return {"error": "URL not found"}
    return {"long_url": url_db[short_url]}
