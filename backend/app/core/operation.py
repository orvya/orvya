from uuid import uuid4

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response


class OperationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        operation_id = str(uuid4())
        request.state.operation_id = operation_id
        response = await call_next(request)
        response.headers["X-Orvya-Operation-Id"] = operation_id
        return response
