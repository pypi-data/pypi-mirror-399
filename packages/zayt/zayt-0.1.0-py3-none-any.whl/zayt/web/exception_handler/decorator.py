from collections.abc import Awaitable, Callable
from typing import NamedTuple, TypeAlias

from asgikit import Request

ATTRIBUTE_EXCEPTION_HANDLER = "__zayt_exception_handler__"

ExceptionHandlerType: TypeAlias = Callable[[Request, BaseException, ...], Awaitable]


class ExceptionHandlerInfo(NamedTuple):
    exception_class: type[BaseException]


def exception_handler(exc: type[BaseException]):
    assert issubclass(exc, BaseException)

    def inner(handler: ExceptionHandlerType):
        setattr(
            handler,
            ATTRIBUTE_EXCEPTION_HANDLER,
            ExceptionHandlerInfo(exception_class=exc),
        )
        return handler

    return inner
