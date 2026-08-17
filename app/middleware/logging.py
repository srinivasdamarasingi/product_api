import time

from fastapi import Request

from app.utils.logger import logger


async def log_requests(
    request: Request,
    call_next
):

    start_time = time.time()

    logger.info(
        f"Incoming Request: {request.method} {request.url.path}"
    )

    response = await call_next(request)

    process_time = round(
        (time.time() - start_time) * 1000,
        2
    )

    logger.info(
        f"Completed Request: "
        f"{request.method} "
        f"{request.url.path} | "
        f"Status={response.status_code} | "
        f"Time={process_time} ms"
    )

    return response