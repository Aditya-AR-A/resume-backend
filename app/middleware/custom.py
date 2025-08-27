import logging
import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Custom logging middleware to log all requests"""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Log request
        logger.info(f"Request: {request.method} {request.url}")

        # Process request
        response = await call_next(request)

        # Calculate processing time
        process_time = time.time() - start_time

        # Log response
        logger.info(".2f")

        return response


class CORSMiddleware:
    """Custom CORS middleware (FastAPI has built-in, but this is for customization)"""

    def __init__(self, app, allow_origins: list = None):
        self.app = app
        self.allow_origins = allow_origins or ["*"]

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def add_cors_headers(message):
            if message["type"] == "http.response.start":
                headers = message.get("headers", [])
                headers.append([b"access-control-allow-origin", b"*"])
                headers.append([b"access-control-allow-methods", b"GET, POST, PUT, DELETE, OPTIONS"])
                headers.append([b"access-control-allow-headers", b"*"])
            await send(message)

        await self.app(scope, receive, add_cors_headers)
