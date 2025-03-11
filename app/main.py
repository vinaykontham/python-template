import logging
import os
import hashlib
from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from authlib.integrations.starlette_client import OAuth
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User, URL
from app.auth import router as auth_router
from app.routes import router as api_router
from pydantic import BaseModel


# Initialize FastAPI app
app = FastAPI()

# Session Middleware for authentication
app.add_middleware(SessionMiddleware, secret_key="your_secret_key")

# OAuth Setup (GitHub Login)
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

oauth = OAuth()
oauth.register(
    name="github",
    client_id=GITHUB_CLIENT_ID,
    client_secret=GITHUB_CLIENT_SECRET,
    authorize_url="https://github.com/login/oauth/authorize",
    access_token_url="https://github.com/login/oauth/access_token",
    client_kwargs={"scope": "user:email"},
)

# Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Serve static files (CSS, JS, etc.)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Serve HTML templates (UI)
templates = Jinja2Templates(directory="app/templates")

# In-memory URL storage (for demonstration)
url_db = {}

# Pydantic Model for URL shortening requests
class ShortenRequest(BaseModel):
    long_url: str

# 🔹 Homepage - Redirects to login if user is not authenticated
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """ Redirect to login page if user is not authenticated """
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/auth/login")

    return templates.TemplateResponse("index.html", {"request": request, "user": user})

# 🔹 GitHub Login Route
@app.get("/auth/login")
async def login(request: Request):
    """ Redirects user to GitHub login """
    return await oauth.github.authorize_redirect(request, "http://localhost:8000/auth/callback")

# 🔹 GitHub OAuth Callback
@app.get("/auth/callback")
async def auth_callback(request: Request, db: Session = Depends(get_db)):
    """ Handles GitHub OAuth callback and stores user data """
    token = await oauth.github.authorize_access_token(request)
    user_data = await oauth.github.get("https://api.github.com/user", token=token)
    user_json = user_data.json()

    # Store user details in DB if not exists
    existing_user = db.query(User).filter(User.id == str(user_json["id"])).first()
    if not existing_user:
        new_user = User(
            id=str(user_json["id"]),
            name=user_json["name"],
            email=user_json.get("email", ""),
            avatar_url=user_json.get("avatar_url", "")
        )
        db.add(new_user)
        db.commit()

    request.session["user"] = user_json
    return RedirectResponse(url="/")

# 🔹 Logout Route
@app.get("/logout")
async def logout(request: Request):
    """ Clears session and logs user out """
    request.session.clear()
    return RedirectResponse(url="/auth/login")

# 🔹 Shorten URL Endpoint
@app.post("/shorten/")
def shorten_url(request: ShortenRequest):
    """ Generates a short URL """
    short_hash = hashlib.md5(request.long_url.encode()).hexdigest()[:6]
    url_db[short_hash] = request.long_url
    return {"short_url": short_hash}

# 🔹 Redirect to Original URL
@app.get("/{short_url}")
def redirect_url(short_url: str):
    """ Redirects from short URL to original URL """
    if short_url not in url_db:
        return {"error": "URL not found"}
    return {"long_url": url_db[short_url]}

# Register routes
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(api_router, tags=["API"])

# Setup Logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
