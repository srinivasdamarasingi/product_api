from unittest.mock import patch, MagicMock


def test_celery_task_submission(client):

    fake_task = MagicMock()
    fake_task.id = "test-task-123"

    with patch(
        "app.routers.auth.long_running_task.delay",
        return_value=fake_task
    ) as mock_delay:

        response = client.post("/auth/celery-test")

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Task Submitted"
    assert data["task_id"] == "test-task-123"

    mock_delay.assert_called_once_with("Srinivasa")


def test_celery_task_failure(error_client):

    with patch(
        "app.routers.auth.long_running_task.delay",
        side_effect=Exception("Celery broker unavailable")
    ):

        response = error_client.post("/auth/celery-test")

    assert response.status_code == 500