from fastapi.testclient import TestClient
from app.main import app



client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "FastAPI Template Ready"}

def test_shorten_url():
    long_url = "https://www.example.com/some/long/url"
    response = client.post("/shorten/", json={"long_url": long_url})
    assert response.status_code == 200
    assert "short_url" in response.json()

def test_redirect_url():
    long_url = "https://www.example.com/some/long/url"
    response = client.post("/shorten/", json={"long_url": long_url})
    short_url = response.json()["short_url"]
    
    redirect_response = client.get(f"/{short_url}")
    assert redirect_response.status_code == 200
    assert redirect_response.json() == {"long_url": long_url}
