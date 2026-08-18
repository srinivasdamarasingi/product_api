from fastapi import APIRouter, HTTPException

from app.services.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerOpenException
)


router = APIRouter(
    prefix="/circuit",
    tags=["Circuit Breaker"]
)


breaker = CircuitBreaker(
    failure_threshold=3,
    recovery_timeout=10
)


@router.get("/")
def circuit_demo():

    try:

        return breaker.call(
            "https://api.example.com"
        )

    except CircuitBreakerOpenException:

        raise HTTPException(
            status_code=503,
            detail="External service temporarily unavailable"
        )