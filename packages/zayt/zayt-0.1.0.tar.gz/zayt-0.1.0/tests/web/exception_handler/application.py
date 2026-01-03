from zayt.web.exception_handler.decorator import exception_handler
from zayt.web.routing.decorator import get


class MyException(Exception):
    pass


class MyBaseException(Exception):
    pass


class DerivedException(MyBaseException):
    pass


@exception_handler(MyException)
async def my_exception_handler(request, exc):
    await request.respond_json({"exception": exc.__class__.__name__})


@exception_handler(BaseException)
async def base_exception_handler(request, exc):
    await request.respond_text(f"handler=base; exception={exc.__class__.__name__}")


@get
async def index(request):
    raise MyException()


@get("base")
async def base(request):
    raise MyBaseException()


@get("derived")
async def derived(request):
    raise DerivedException()
