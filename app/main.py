import logging
import os
import hashlib
from fastapi import FastAPI, Request, Depends
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from app.auth import router as auth_router
from app.routes import router as api_router
from fastapi.responses import RedirectResponse, HTMLResponse
from authlib.integrations.starlette_client import OAuth
from starlette.middleware.sessions import SessionMiddleware
from app.database import SessionLocal, User
from app.models import User


app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="your_secret_key")

# Load secrets from environment variables
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
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """ Redirect to login page if user is not authenticated """
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/auth/login")
    
    return """
    <html>
    <head><title>FastAPI URL Shortener</title></head>
    <body>
        <h2>Welcome, {}</h2>
        <a href="/logout">Logout</a>
    </body>
    </html>
    """.format(user["name"])

@app.get("/auth/login")
async def login(request: Request):
    """ Redirects user to GitHub login """
    return await oauth.github.authorize_redirect(request, "http://localhost:8000/auth/callback")

@app.get("/auth/callback")
async def auth_callback(request: Request, db: Session = Depends(get_db)):
    """Handles GitHub OAuth callback and stores user data"""
    token = await oauth.github.authorize_access_token(request)
    user_data = await oauth.github.get("https://api.github.com/user", token=token)
    user_json = user_data.json()

    # Store user details in DB if not exists
    existing_user = db.query(User).filter(User.id == str(user_json["id"])).first()
    if not existing_user:
        new_user = User(
            id=str(user_json["id"]),
            name=user_json["name"],
            email=user_json["email"],
            avatar_url=user_json["avatar_url"]
        )
        db.add(new_user)
        db.commit()

    request.session["user"] = user_json
    return RedirectResponse(url="/")

@app.get("/logout")
async def logout(request: Request):
    """ Clears session and logs user out """
    request.session.clear()
    return RedirectResponse(url="/auth/login")

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
