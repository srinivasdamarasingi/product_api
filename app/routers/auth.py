from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.users import UserCreate, UserResponse
from app.crud import user as user_crud
from app.schemas.users import UserLogin
from app.security import create_access_token
from app.schemas.users import Token
from app.security import (
    create_access_token,
    get_current_user,
    hash_password,
)
from app.models.user import User
from fastapi.security import OAuth2PasswordRequestForm
from app.services.email_service import send_email
from app.schemas.users import ForgotPasswordRequest
from app.utils.security import (
    generate_reset_token,
    generate_reset_expiry,
)
from datetime import datetime
from app.schemas.users import (
    ForgotPasswordRequest,
    ResetPasswordRequest,
)
from app.utils.logger import logger

from fastapi import APIRouter, BackgroundTasks
import time

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/register", response_model=UserResponse)
async def register(
    user: UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):

    db_user = user_crud.create_user(db, user)

    if db_user is None:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Send welcome email
    background_tasks.add_task(
    send_email,
    db_user.email,
    "Welcome to Product API",
    "welcome_email.html",
    username=db_user.username,
    email=db_user.email,
)

    return db_user

@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    logger.info(f"Login attempt for email: {form_data.username}")

    db_user = user_crud.authenticate_user(
        db,
        form_data.username,
        form_data.password
    )

    if db_user is None:
        logger.warning(f"Failed login attempt for email: {form_data.username}")

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    logger.info(f"Successful login for email: {db_user.email}")

    access_token = create_access_token(
        {"sub": db_user.email}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/me")
def get_me(
    current_user: User = Depends(get_current_user)
):

    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email
    }

@router.post("/forgot-password")
async def forgot_password(
    request: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):

    user = db.query(User).filter(
        User.email == request.email
    ).first()

    if user:
        user.reset_token = generate_reset_token()

        user.reset_token_expiry = generate_reset_expiry()

        db.commit()

        background_tasks.add_task(
        send_email,
        user.email,
        "Reset Your Password",
        "password_reset.html",
        username=user.username,
        reset_link=f"http://localhost:8000/reset-password?token={user.reset_token}",
    )

    return {
        "message": (
            "If an account exists with that email, "
            "a password reset link will be sent."
        )
    }

@router.post("/reset-password")
async def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db),
):

    user = db.query(User).filter(
        User.reset_token == request.token
    ).first()

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Invalid reset token"
        )

    if datetime.utcnow() > user.reset_token_expiry:
        raise HTTPException(
            status_code=400,
            detail="Reset token has expired"
        )

    user.hashed_password = hash_password(
        request.new_password
    )

    user.reset_token = None
    user.reset_token_expiry = None

    db.commit()

    return {
        "message": "Password reset successfully"
    }

""" @router.get("/test-error")
def test_error():
    result = 10 / 0
    return {"result": result} """

def long_running_task():
    print("Task Started...")
    time.sleep(5)
    print("Task Completed...")


@router.get("/background-demo")
def background_demo(background_tasks: BackgroundTasks):

    background_tasks.add_task(long_running_task)

    return {
        "message": "Background task started successfully."
    }

from app.celery_tasks import long_running_task


@router.post("/celery-test")
def celery_test():

    task = long_running_task.delay("Srinivasa")

    return {
        "message": "Task Submitted",
        "task_id": task.id
    }