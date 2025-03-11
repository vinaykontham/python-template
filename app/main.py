import logging
from fastapi import FastAPI, Request, Depends
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import hashlib
from app.auth import router as auth_router
from app.routes import router as api_router
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
import os

app = FastAPI()
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
oauth = OAuth()
oauth.register(
    name="github",
    client_id=GITHUB_CLIENT_ID,
    client_secret=GITHUB_CLIENT_SECRET,
    authorize_url="https://github.com/login/oauth/authorize",
    authorize_params=None,
    access_token_url="https://github.com/login/oauth/access_token",
    access_token_params=None,
    client_kwargs={"scope": "user:email"},
)

@app.get("/auth/login")
async def login(request: Request):
    return await oauth.github.authorize_redirect(request, "http://localhost:8000/auth/callback")

@app.get("/auth/callback")
async def auth_callback(request: Request):
    token = await oauth.github.authorize_access_token(request)
    user = await oauth.github.parse_id_token(request, token)
    return {"user": user}

# Register routes
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(api_router, tags=["API"])

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
