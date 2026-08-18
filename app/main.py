from fastapi import FastAPI

from app.database import Base, engine

from app.models.products import Product
from app.models.category import Category

from app.routers.products import router as product_router
from app.routers.categories import router as category_router
from app.models.user import User
from app.routers.auth import router as auth_router
from fastapi.staticfiles import StaticFiles
from app.routers import email
from app.utils.logger import logger
from app.middleware.logging import log_requests
from app.exceptions.handlers import product_not_found_exception_handler
from app.exceptions.custom_exceptions import ProductNotFoundException
from app.exceptions.handlers import global_exception_handler
from fastapi.exceptions import RequestValidationError
from app.exceptions.handlers import validation_exception_handler
from app.routers.weather import (
    router as weather_router
)

from app.routers.retry import (
    router as retry_router
)
from app.routers.circuit import (
    router as circuit_router
)

logger.info("Application Started Successfully")

app = FastAPI()

app.add_exception_handler(
    ProductNotFoundException,
    product_not_found_exception_handler
)

app.add_exception_handler(
    Exception,
    global_exception_handler
)

app.add_exception_handler(
    ProductNotFoundException,
    product_not_found_exception_handler
)

app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler
)

app.add_exception_handler(
    Exception,
    global_exception_handler
)

app.middleware("http")(log_requests)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

#Base.metadata.create_all(bind=engine)

# Register both routers
app.include_router(product_router)
app.include_router(category_router)
app.include_router(auth_router)
app.include_router(email.router)
app.include_router(
    weather_router
)
app.include_router(
    retry_router
)
app.include_router(
    circuit_router
)

@app.get("/")
def home():
    return {
        "message": "Welcome to Product API"
    }