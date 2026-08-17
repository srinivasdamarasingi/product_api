def test_login_success(client, test_admin):

    response = client.post(
        "/auth/login",
        data={
            "username": test_admin.email,
            "password": "TestPassword123!"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, test_admin):

    response = client.post(
        "/auth/login",
        data={
            "username": test_admin.email,
            "password": "WrongPassword123!"
        }
    )

    assert response.status_code == 401

    assert response.json()["detail"] == "Invalid email or password"


def test_login_unknown_user(client):

    response = client.post(
        "/auth/login",
        data={
            "username": "unknown@example.com",
            "password": "TestPassword123!"
        }
    )

    assert response.status_code == 401

    assert response.json()["detail"] == "Invalid email or password"


def test_get_me_authenticated(client, test_admin):

    login_response = client.post(
        "/auth/login",
        data={
            "username": test_admin.email,
            "password": "TestPassword123!"
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["email"] == test_admin.email
    assert data["username"] == test_admin.username


def test_get_me_without_authentication(client):

    response = client.get("/auth/me")

    assert response.status_code == 401


def test_get_me_invalid_token(client):

    response = client.get(
        "/auth/me",
        headers={
            "Authorization": "Bearer invalid-token"
        }
    )

    assert response.status_code == 401

from unittest.mock import patch


def test_register_sends_welcome_email(client):

    payload = {
        "username": "mock_user",
        "email": "mock_user@example.com",
        "password": "TestPassword123!"
    }

    with patch("app.routers.auth.send_email") as mock_email:

        response = client.post(
            "/auth/register",
            json=payload
        )

    assert response.status_code == 200

    mock_email.assert_called_once()