import logging
from fastapi.testclient import TestClient
from app.main import app

# Configure logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

client = TestClient(app)

def test_root():
    """Test if the home page loads successfully."""
    response = client.get("/")
    assert response.status_code == 200
    assert "FastAPI URL Shortener" in response.text  # Check for expected text in HTML

def test_shorten_url():
    """Test the URL shortening endpoint."""
    long_url = "https://www.example.com/some/long/url"
    response = client.post("/shorten/", json={"long_url": long_url})

    logger.debug(f"Shorten URL Response: {response.json()}")  # Debugging

    assert response.status_code == 200
    assert "short_url" in response.json()

def test_redirect_url():
    """Test the URL redirection functionality."""
    long_url = "https://www.example.com/some/long/url"
    response = client.post("/shorten/", json={"long_url": long_url})

    logger.debug(f"Shorten URL Response: {response.json()}")  # Debugging

    short_url = response.json()["short_url"]
    redirect_response = client.get(f"/{short_url}")

    logger.debug(f"Redirect Response: {redirect_response.json()}")  # Debugging

    assert redirect_response.status_code == 200
    assert redirect_response.json() == {"long_url": long_url}
