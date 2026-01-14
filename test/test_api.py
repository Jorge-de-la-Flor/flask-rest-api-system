import os
import sys
import pytest
from flask_api_system import app, db_service

# Se añade la raíz del proyecto al sys.path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))


@pytest.fixture(autouse=True)
def setup_test_db(tmp_path, monkeypatch):
    # Usar una base de datos SQLite temporal para los tests
    test_db_path = tmp_path / "test_api_system.db"
    monkeypatch.setattr(db_service, "db_path", str(test_db_path))
    db_service.init_database()
    yield
    # No hace falta cleanup extra, tmp_path se borra solo

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_status_ok(client):
    resp = client.get("/api/status")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "active"

def test_register_and_login(client):
    # Register
    resp = client.post(
        "/api/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
        },
    )
    assert resp.status_code == 201

    # Login
    resp = client.post(
        "/api/login",
        json={
            "username": "testuser",
            "password": "testpass123",
        },
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert "token" in data

def test_protected_operations_flow(client):
    # Register
    client.post(
        "/api/register",
        json={
            "username": "testuser2",
            "email": "test2@example.com",
            "password": "testpass123",
        },
    )

    # Login
    resp = client.post(
        "/api/login",
        json={
            "username": "testuser2",
            "password": "testpass123",
        },
    )
    token = resp.get_json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create operation
    resp = client.post(
        "/api/operations",
        json={"operation_type": "test", "data": {"foo": "bar"}},
        headers=headers,
    )
    assert resp.status_code == 201

    # Get operations
    resp = client.get("/api/operations", headers=headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["count"] >= 1
