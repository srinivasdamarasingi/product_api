from unittest.mock import patch


def test_rate_limit_allows_request(client):

    with patch(
        "app.services.rate_limiter.redis_client"
    ) as mock_redis:

        mock_redis.incr.return_value = 1

        response = client.get(
            "/rate-limit/"
        )

    assert response.status_code == 200
    
    assert response.headers["X-RateLimit-Limit"] == "5"

    assert response.json() == {
        "message": "Request allowed"
    }

    mock_redis.expire.assert_called_once()

def test_rate_limit_blocks_request(client):

    with patch(
        "app.services.rate_limiter.redis_client"
    ) as mock_redis:

        mock_redis.incr.return_value = 6

        response = client.get(
            "/rate-limit/"
        )

    assert response.status_code == 429

    assert response.headers["Retry-After"] == "60"

    assert response.json()["detail"] == (
        "Too many requests"
    )


def test_user_rate_limit_normal_user(
    user_client,
    test_user
):

    with patch(
        "app.services.rate_limiter.redis_client"
    ) as mock_redis:

        mock_redis.incr.return_value = 1

        response = user_client.get(
            "/rate-limit/user"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["user"] == test_user.email
    assert data["limit"] == 5

    assert response.headers[
        "X-RateLimit-Limit"
    ] == "5"

def test_user_rate_limit_admin(
    admin_client,
    test_admin
):

    with patch(
        "app.services.rate_limiter.redis_client"
    ) as mock_redis:

        mock_redis.incr.return_value = 1

        response = admin_client.get(
            "/rate-limit/user"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["user"] == test_admin.email
    assert data["limit"] == 10

    assert response.headers[
        "X-RateLimit-Limit"
    ] == "10"

def test_user_rate_limit_blocks_normal_user(
    user_client
):

    with patch(
        "app.services.rate_limiter.redis_client"
    ) as mock_redis:

        mock_redis.incr.return_value = 6

        response = user_client.get(
            "/rate-limit/user"
        )

    assert response.status_code == 429

    assert response.json()["detail"] == (
        "Too many requests"
    )

    assert response.headers[
        "Retry-After"
    ] == "60"

def test_user_rate_limit_requires_authentication(
    client
):

    response = client.get(
        "/rate-limit/user"
    )

    assert response.status_code == 401

def test_rate_limit_sequential_requests(client):

    with patch(
        "app.services.rate_limiter.redis_client"
    ) as mock_redis:

        mock_redis.incr.side_effect = [
            1, 2, 3, 4, 5, 6
        ]

        status_codes = []

        for _ in range(6):

            response = client.get(
                "/rate-limit/"
            )

            status_codes.append(
                response.status_code
            )

    assert status_codes == [
        200,
        200,
        200,
        200,
        200,
        429
    ]

    assert mock_redis.incr.call_count == 6

    assert mock_redis.expire.call_count == 1