"""
Tests for health check endpoints.
Phase 6: Backend testing.
"""

import pytest
from fastapi.testclient import TestClient


def test_basic_health_check(client: TestClient):
    """Test basic health check endpoint."""
    response = client.get("/api/v1/health/")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "version" in data
    assert "environment" in data


def test_liveness_check(client: TestClient):
    """Test Kubernetes liveness probe."""
    response = client.get("/api/v1/health/live")

    assert response.status_code == 200
    data = response.json()

    assert data["alive"] is True
    assert "timestamp" in data


def test_readiness_check(client: TestClient):
    """Test Kubernetes readiness probe."""
    response = client.get("/api/v1/health/ready")

    assert response.status_code == 200
    data = response.json()

    # May be True or False depending on DB connection
    assert "ready" in data
    assert "timestamp" in data
