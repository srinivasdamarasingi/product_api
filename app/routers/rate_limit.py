from fastapi import (
    APIRouter,
    HTTPException,
    Request,
    Response,
    Depends
)

from app.services.rate_limiter import is_rate_limited
from app.security import get_current_user
from app.models.user import User


router = APIRouter(
    prefix="/rate-limit",
    tags=["Rate Limiting"]
)


# ============================================================
# IP-BASED RATE LIMIT
# ============================================================

@router.get("/")
def rate_limit_demo(
    request: Request,
    response: Response
):

    client_ip = (
        request.client.host
        if request.client
        else "unknown"
    )

    limit = 5

    if is_rate_limited(
        key=client_ip,
        limit=limit,
        window_seconds=60
    ):
        raise HTTPException(
            status_code=429,
            detail="Too many requests",
            headers={
                "Retry-After": "60"
            }
        )

    response.headers["X-RateLimit-Limit"] = str(limit)

    return {
        "message": "Request allowed"
    }


# ============================================================
# USER/JWT-BASED RATE LIMIT
# ============================================================

@router.get("/user")
def user_rate_limit_demo(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user)
):

    if current_user.is_admin:
        limit = 10
    else:
        limit = 5

    key = f"user:{current_user.email}"

    if is_rate_limited(
        key=key,
        limit=limit,
        window_seconds=60
    ):
        raise HTTPException(
            status_code=429,
            detail="Too many requests",
            headers={
                "Retry-After": "60"
            }
        )

    response.headers["X-RateLimit-Limit"] = str(limit)

    return {
        "message": "Request allowed",
        "user": current_user.email,
        "limit": limit
    }