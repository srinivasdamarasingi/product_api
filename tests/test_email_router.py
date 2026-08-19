from unittest.mock import AsyncMock, patch


def test_email_endpoint(client):

    with patch(
        "app.routers.email.send_email",
        new_callable=AsyncMock
    ) as mock_send_email:

        response = client.post(
            "/email/test"
        )

    assert response.status_code == 200

    assert response.json() == {
        "message": "Email sent successfully"
    }

    mock_send_email.assert_awaited_once()