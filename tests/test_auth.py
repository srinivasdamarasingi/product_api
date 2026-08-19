from unittest.mock import patch
from datetime import datetime, timedelta

from app.security import verify_password

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

def test_register_duplicate_email(
    client,
    test_user
):

    response = client.post(
        "/auth/register",
        json={
            "username": "another_user",
            "email": test_user.email,
            "password": "TestPassword123!"
        }
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "Email already registered"
    )

def test_forgot_password_existing_user(
    client,
    test_user,
    db_session
):

    with patch(
        "app.routers.auth.send_email"
    ) as mock_email:

        response = client.post(
            "/auth/forgot-password",
            json={
                "email": test_user.email
            }
        )

    assert response.status_code == 200

    assert response.json()["message"] == (
        "If an account exists with that email, "
        "a password reset link will be sent."
    )

    db_session.refresh(test_user)

    assert test_user.reset_token is not None
    assert test_user.reset_token_expiry is not None

    mock_email.assert_called_once()

def test_forgot_password_unknown_user(
    client
):

    with patch(
        "app.routers.auth.send_email"
    ) as mock_email:

        response = client.post(
            "/auth/forgot-password",
            json={
                "email": "doesnotexist@example.com"
            }
        )

    assert response.status_code == 200

    assert response.json()["message"] == (
        "If an account exists with that email, "
        "a password reset link will be sent."
    )

    mock_email.assert_not_called()

def test_reset_password_success(
    client,
    test_user,
    db_session
):

    test_user.reset_token = "valid-reset-token"

    test_user.reset_token_expiry = (
        datetime.utcnow()
        + timedelta(minutes=30)
    )

    db_session.commit()

    response = client.post(
        "/auth/reset-password",
        json={
            "token": "valid-reset-token",
            "new_password": "NewPassword123!"
        }
    )

    assert response.status_code == 200

    assert response.json()["message"] == (
        "Password reset successfully"
    )

    db_session.refresh(test_user)

    assert verify_password(
        "NewPassword123!",
        test_user.hashed_password
    )

    assert test_user.reset_token is None
    assert test_user.reset_token_expiry is None

def test_reset_password_invalid_token(
    client
):

    response = client.post(
        "/auth/reset-password",
        json={
            "token": "invalid-reset-token",
            "new_password": "NewPassword123!"
        }
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "Invalid reset token"
    )

def test_reset_password_expired_token(
    client,
    test_user,
    db_session
):

    test_user.reset_token = "expired-token"

    test_user.reset_token_expiry = (
        datetime.utcnow()
        - timedelta(minutes=10)
    )

    db_session.commit()

    response = client.post(
        "/auth/reset-password",
        json={
            "token": "expired-token",
            "new_password": "NewPassword123!"
        }
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "Reset token has expired"
    )