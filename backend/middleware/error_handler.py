from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
import logging

logger = logging.getLogger(__name__)

async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Global handler for HTTP exceptions."""
    logger.warning(f"HTTP Exception: {exc.detail} for path {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": True, "detail": exc.detail},
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Global handler for validation exceptions."""
    logger.error(f"Validation Error: {exc.errors()} for path {request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": True, "detail": exc.errors()},
    )

async def generic_exception_handler(request: Request, exc: Exception):
    """Global handler for unhandled generic exceptions."""
    logger.error(f"Unhandled Exception: {str(exc)} for path {request.url.path}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": True, "detail": "An internal server error occurred."},
    )
