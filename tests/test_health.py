
from unittest.mock import patch, MagicMock

from sqlalchemy.exc import OperationalError


def test_liveness(client):
    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


def test_readiness_success(client):
    mock_connection = MagicMock()

    mock_context = MagicMock()
    mock_context.__enter__.return_value = mock_connection

    with patch(
        "app.routers.health.engine.connect",
        return_value=mock_context
    ):
        response = client.get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}

    mock_connection.execute.assert_called_once()


def test_readiness_database_failure(client):
    database_error = OperationalError(
        "SELECT 1",
        {},
        Exception("Simulated database failure")
    )

    with patch(
        "app.routers.health.engine.connect",
        side_effect=database_error
    ):
        response = client.get("/health/ready")

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Database unavailable"
    }
