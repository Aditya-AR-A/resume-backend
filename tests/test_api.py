import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["version"] == "1.0.0"


def test_health_endpoint():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_intro_endpoint():
    """Test the intro data endpoint"""
    response = client.get("/api/intro")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data


def test_jobs_endpoint():
    """Test the jobs data endpoint"""
    response = client.get("/api/jobs")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data


def test_projects_endpoint():
    """Test the projects data endpoint"""
    response = client.get("/api/projects")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data


def test_ai_status_endpoint():
    """Test the AI status endpoint"""
    response = client.get("/ai/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "offline"
    assert "components" in data


# Placeholder tests for AI endpoints (will be updated when implemented)
def test_ai_analyze_endpoint():
    """Test the AI analyze endpoint (placeholder)"""
    response = client.post("/ai/analyze", json={"content": "test content"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "placeholder" in data["data"]["status"]


def test_ai_generate_endpoint():
    """Test the AI generate endpoint (placeholder)"""
    response = client.post("/ai/generate", json={"prompt": "test prompt"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "placeholder" in data["data"]["status"]
