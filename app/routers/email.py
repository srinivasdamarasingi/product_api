from fastapi import APIRouter

from app.services.email_service import send_email


router = APIRouter(
    prefix="/email",
    tags=["Email"]
)


@router.post("/test")
async def test_email():

    await send_email(
        to_email="srinivas.damarasingi@gmail.com",
        subject="Welcome to Product API",
        template_name="welcome_email.html",
        username="Srinivas",
        email="srinivas.damarasingi@gmail.com",
    )

    return {
        "message": "Email sent successfully"
    }