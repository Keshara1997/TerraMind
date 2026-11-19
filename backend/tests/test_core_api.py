"""Smoke tests for auth, projects, and areas against a running API.

Set TEST_API_URL (default http://127.0.0.1:8000) or skip when unreachable.
"""

import os
import uuid

import httpx

BASE = os.environ.get("TEST_API_URL", "http://127.0.0.1:8000").rstrip("/")
API = f"{BASE}/api/v1"


def _api_reachable() -> bool:
    try:
        response = httpx.get(f"{BASE}/health", timeout=2.0)
        return response.status_code == 200
    except httpx.HTTPError:
        return False


def test_health():
    if not _api_reachable():
        return
    response = httpx.get(f"{BASE}/health", timeout=5.0)
    assert response.status_code == 200
    assert response.json().get("status") == "healthy"


def test_auth_project_area_flow():
    if not _api_reachable():
        return

    email = f"test_{uuid.uuid4().hex[:12]}@example.com"
    password = "TestPass123!"

    with httpx.Client(base_url=BASE, timeout=30.0) as client:
        register = client.post(
            f"{API}/auth/register",
            json={
                "email": email,
                "full_name": "Core API Test",
                "password": password,
            },
        )
        assert register.status_code == 201, register.text

        login = client.post(
            f"{API}/auth/login",
            json={"email": email, "password": password},
        )
        assert login.status_code == 200, login.text
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        me = client.get(f"{API}/auth/me", headers=headers)
        assert me.status_code == 200
        assert me.json()["email"] == email

        project = client.post(
            f"{API}/projects/",
            headers=headers,
            json={"name": "Stabilization test project"},
        )
        assert project.status_code == 201, project.text
        project_id = project.json()["id"]

        listed = client.get(f"{API}/projects/", headers=headers)
        assert listed.status_code == 200
        assert any(item["id"] == project_id for item in listed.json())

        area = client.post(
            f"{API}/projects/{project_id}/areas/",
            headers=headers,
            json={
                "name": "Test polygon",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [79.85, 6.90],
                            [79.86, 6.90],
                            [79.86, 6.91],
                            [79.85, 6.91],
                            [79.85, 6.90],
                        ]
                    ],
                },
            },
        )
        assert area.status_code == 201, area.text
        area_id = area.json()["id"]
        assert area.json()["area_sq_km"] > 0

        areas = client.get(
            f"{API}/projects/{project_id}/areas/",
            headers=headers,
        )
        assert areas.status_code == 200
        assert any(item["id"] == area_id for item in areas.json())

        deleted = client.delete(
            f"{API}/projects/{project_id}",
            headers=headers,
        )
        assert deleted.status_code == 204