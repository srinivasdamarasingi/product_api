from fastapi import Request
from fastapi.responses import JSONResponse

from app.exceptions.custom_exceptions import ProductNotFoundException
from app.utils.logger import logger
from fastapi.exceptions import RequestValidationError

async def product_not_found_exception_handler(
    request: Request,
    exc: ProductNotFoundException
):
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "message": exc.message
        }
    )

async def global_exception_handler(
    request: Request,
    exc: Exception
):
    logger.exception(
        f"Unhandled Exception: {str(exc)}"
    )

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal Server Error"
        }
    )

async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    errors = []

    for error in exc.errors():

        field = ".".join(
            str(item)
            for item in error["loc"]
            if item != "body"
        )

        errors.append(
            {
                "field": field,
                "message": error["msg"]
            }
        )

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Validation Failed",
            "errors": errors
        }
    )