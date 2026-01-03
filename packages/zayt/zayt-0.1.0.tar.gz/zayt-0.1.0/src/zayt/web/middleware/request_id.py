import uuid

from structlog.contextvars import bind_contextvars, unbind_contextvars

from zayt.util.asgi import get_header


async def request_id_middleware(app):
    async def handler(scope, receive, send):
        request_id = get_header("x-request-id", scope) or str(uuid.uuid4())

        try:
            bind_contextvars(request_id=request_id)
            await app(scope, receive, send)
        finally:
            unbind_contextvars("request_id")

    return handler
