from fastapi import APIRouter

from app.services.retry_service import (
    fetch_data
)

router = APIRouter(
    prefix="/retry",
    tags=["Retry"]
)


@router.get("/")
def retry_demo():

    return fetch_data(
        "https://api.example.com"
    )