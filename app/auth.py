from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2AuthorizationCodeBearer
from starlette.requests import Request
import httpx
import logging
from app.config import OAUTH_CLIENT_ID, OAUTH_CLIENT_SECRET, OAUTH_REDIRECT_URI, OAUTH_PROVIDER_URL

# Logger setup
logger = logging.getLogger(__name__)

router = APIRouter()

# OAuth2 Scheme
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"{OAUTH_PROVIDER_URL}/o/oauth2/auth",
    tokenUrl=f"{OAUTH_PROVIDER_URL}/o/oauth2/token"
)

@router.get("/auth/login")
async def login():
    """Redirect user to OAuth login page."""
    return {
        "login_url": f"{OAUTH_PROVIDER_URL}/o/oauth2/auth"
                      f"?client_id={OAUTH_CLIENT_ID}"
                      f"&redirect_uri={OAUTH_REDIRECT_URI}"
                      f"&response_type=code"
                      f"&scope=email profile"
    }

@router.get("/auth/callback")
async def callback(request: Request, code: str):
    """OAuth2 Callback to exchange code for an access token."""
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            f"{OAUTH_PROVIDER_URL}/o/oauth2/token",
            data={
                "client_id": OAUTH_CLIENT_ID,
                "client_secret": OAUTH_CLIENT_SECRET,
                "code": code,
                "redirect_uri": OAUTH_REDIRECT_URI,
                "grant_type": "authorization_code"
            }
        )
        
        if token_response.status_code != 200:
            logger.error(f"OAuth2 token exchange failed: {token_response.text}")
            raise HTTPException(status_code=400, detail="OAuth authentication failed")

        token_data = token_response.json()
        access_token = token_data["access_token"]
        
        # Fetch user info
        user_response = await client.get(
            f"{OAUTH_PROVIDER_URL}/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if user_response.status_code != 200:
            logger.error(f"Failed to fetch user info: {user_response.text}")
            raise HTTPException(status_code=400, detail="User info retrieval failed")

        user_info = user_response.json()
        logger.info(f"Authenticated user: {user_info}")

        return {"access_token": access_token, "user": user_info}
