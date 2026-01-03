from http import HTTPStatus


class HTTPStatusException(Exception):
    status: HTTPStatus

    def __init__(
        self,
        *,
        status: HTTPStatus | None = None,
        headers: dict[str, str] | None = None,
    ):
        if status:
            self.status = status

        self.headers = headers or {}


class WebSocketException(Exception):
    def __init__(self, status: int, reason: str = None) -> None:
        self.code = status
        self.reason = reason or ""


class HTTPBadRequestException(HTTPStatusException):
    status = HTTPStatus.BAD_REQUEST


class HTTPNotFoundException(HTTPStatusException):
    status = HTTPStatus.NOT_FOUND


class HTTPUnauthorizedException(HTTPStatusException):
    status = HTTPStatus.UNAUTHORIZED


class HTTPForbiddenException(HTTPStatusException):
    status = HTTPStatus.FORBIDDEN


class HTTPInternalServerException(HTTPStatusException):
    status = HTTPStatus.INTERNAL_SERVER_ERROR
