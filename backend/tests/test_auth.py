from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)
HAL = {"Accept": "application/hal+json"}


def test_current_user_defaults_to_local_anonymous_when_auth_is_disabled(monkeypatch):
    monkeypatch.delenv("AUTH_API_REQUIRED", raising=False)

    response = client.get("/v1/me", headers=HAL)

    assert response.status_code == 200
    assert response.json()["auth_type"] == "disabled"
    assert response.json()["username"] == "local-anonymous"


def test_current_user_uses_authentik_proxy_headers(monkeypatch):
    monkeypatch.setenv("AUTH_API_REQUIRED", "true")

    response = client.get(
        "/v1/me",
        headers={
            **HAL,
            "X-authentik-username": "simon",
            "X-authentik-email": "simon@example.test",
            "X-authentik-groups": "admin,operator",
        },
    )

    assert response.status_code == 200
    assert response.json()["username"] == "simon"
    assert response.json()["email"] == "simon@example.test"
    assert response.json()["roles"] == ["admin", "operator"]


def test_api_requires_identity_when_auth_is_enabled(monkeypatch):
    monkeypatch.setenv("AUTH_API_REQUIRED", "true")

    response = client.get("/v1/opportunities", headers=HAL)

    assert response.status_code == 401


def test_service_token_can_call_api_when_auth_is_enabled(monkeypatch):
    monkeypatch.setenv("AUTH_API_REQUIRED", "true")
    monkeypatch.setenv("AUTH_SERVICE_TOKEN", "test-service-token")

    response = client.get(
        "/v1/opportunities",
        headers={**HAL, "Authorization": "Bearer test-service-token"},
    )

    assert response.status_code == 200
