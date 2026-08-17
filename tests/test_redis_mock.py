from unittest.mock import MagicMock


def test_mock_redis():

    redis_client = MagicMock()

    redis_client.set.return_value = True

    redis_client.get.return_value = "Srinivas"

    assert redis_client.set(
        "name",
        "Srinivas"
    ) is True

    assert redis_client.get(
        "name"
    ) == "Srinivas"

    redis_client.set.assert_called_once_with(
        "name",
        "Srinivas"
    )

    redis_client.get.assert_called_once_with(
        "name"
    )