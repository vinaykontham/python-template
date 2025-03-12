import logging
from fastapi.testclient import TestClient
from app.main import app

# Configure logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

client = TestClient(app)

def test_root():
    """Test if homepage redirects to login when user is unauthenticated."""
    response = client.get("/")
    logger.debug(f"Root Response Status: {response.status_code}")
    
    assert response.status_code in [302, 307]  # Expect redirect to /auth/login
    assert "/auth/login" in response.headers["location"]  # Check redirect URL

def test_shorten_url():
    """Test the URL shortening endpoint."""
    long_url = "https://www.example.com/some/long/url"
    response = client.post("/shorten/", json={"long_url": long_url})

    logger.debug(f"Shorten URL Response: {response.json()}")

    assert response.status_code == 200
    assert "short_url" in response.json()
    assert len(response.json()["short_url"]) > 0  # Ensure non-empty short URL

def test_redirect_url():
    """Test the URL redirection functionality."""
    long_url = "https://www.example.com/some/long/url"
    response = client.post("/shorten/", json={"long_url": long_url})

    logger.debug(f"Shorten URL Response: {response.json()}")

    short_url = response.json()["short_url"]
    redirect_response = client.get(f"/{short_url}", follow_redirects=False)

    logger.debug(f"Redirect Response Status: {redirect_response.status_code}")
    
    assert redirect_response.status_code in [302, 307]  # Expect redirect
    assert "location" in redirect_response.headers  # Ensure redirection
    assert redirect_response.headers["location"] == long_url  # Check if redirected correctly
