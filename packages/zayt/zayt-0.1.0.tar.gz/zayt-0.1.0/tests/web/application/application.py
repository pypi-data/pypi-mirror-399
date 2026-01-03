from asgikit import Request
from zayt.web import get, websocket


@get
async def index(request: Request):
    await request.respond_text("Ok")


@websocket("exception/new")
async def ws_exception_new(request: Request):
    raise Exception("NEW")


@websocket("exception/accepted")
async def ws_exception_accepted(request: Request):
    _ws = await request.upgrade()
    raise Exception("accepted")
