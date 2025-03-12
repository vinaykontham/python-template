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
from app.database import SessionLocal, Base, engine
from app.models import User, URL
from app.auth import router as auth_router
from app.routes import router as api_router
from pydantic import BaseModel

logger = logging.getLogger(__name__)
# Initialize FastAPI app
app = FastAPI()

# Middleware for session management
SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "random_default_key"))

# CORS Middleware (Optional: If UI is hosted separately)
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Initialization (Ensures Tables Are Created)
Base.metadata.create_all(bind=engine)

# OAuth Setup (GitHub Login)
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
CALLBACK_URL = os.getenv("CALLBACK_URL", "http://localhost:8000/auth/callback")

if not GITHUB_CLIENT_ID or not GITHUB_CLIENT_SECRET:
    raise ValueError("GitHub OAuth credentials are missing!")

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

# Model for URL shortening request
class ShortenRequest(BaseModel):
    long_url: str

# 🔹 Homepage - Redirects to login if user is not authenticated
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """ Debugging logs for authentication """
    logger.debug(f"Session contents: {request.session}")  # Log session for debugging

    user = request.session.get("user")
    if not user:
        logger.debug("User is NOT authenticated, redirecting to login.")
        return HTMLResponse(content="<h1>401 Unauthorized - Please login</h1>", status_code=401)

    logger.debug(f"User authenticated: {user}")
    return templates.TemplateResponse("index.html", {"request": request, "user": user})

# 🔹 GitHub Login Route
@app.get("/auth/login")
async def login(request: Request):
    """ Redirects user to GitHub login """
    return await oauth.github.authorize_redirect(request, CALLBACK_URL)

# 🔹 GitHub OAuth Callback
@app.get("/auth/callback")
async def auth_callback(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.github.authorize_access_token(request)
        if not token:
            return RedirectResponse(url="/auth/login?error=oauth_failed")

        user_data = await oauth.github.get("https://api.github.com/user", token=token)
        user_json = user_data.json()

        if "id" not in user_json:
            return RedirectResponse(url="/auth/login?error=invalid_user")

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

        logger.debug(f"Session before setting user: {request.session}")  # Log session before setting user
        request.session["user"] = user_json  # Store user info in session
        logger.debug(f"Session after setting user: {request.session}")  # Log session after setting user

        return RedirectResponse(url="/")

    except Exception as e:
        logger.error(f"OAuth Callback Error: {str(e)}")  # Use logger for error reporting

        return RedirectResponse(url=f"/auth/login?error=unexpected_error&message={str(e)}")

# 🔹 Logout Route
@app.get("/logout")
async def logout(request: Request):
    """ Clears session and logs user out """
    request.session.clear()
    return RedirectResponse(url="/auth/login")

# 🔹 Shorten URL Endpoint
@app.post("/shorten/")
def shorten_url(request: ShortenRequest, db: Session = Depends(get_db)):
    """ Generates a short URL and stores it in the database """
    short_hash = hashlib.md5(request.long_url.encode()).hexdigest()[:6]
    
    # Check if URL already exists
    existing_url = db.query(URL).filter(URL.short_url == short_hash).first()
    if existing_url:
        return {"short_url": existing_url.short_url}

    new_url = URL(short_url=short_hash, long_url=request.long_url)
    db.add(new_url)
    db.commit()
    
    return {"short_url": short_hash}

# 🔹 Redirect to Original URL
@app.get("/{short_url}")
def redirect_url(short_url: str, db: Session = Depends(get_db)):
    url_entry = db.query(URL).filter(URL.short_url == short_url).first()
    if not url_entry:
        return HTMLResponse("<h1>404 - URL Not Found</h1>", status_code=404)
    
    return RedirectResponse(url=url_entry.long_url, status_code=302)

# Register routes
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(api_router, tags=["API"])

# Setup Logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
