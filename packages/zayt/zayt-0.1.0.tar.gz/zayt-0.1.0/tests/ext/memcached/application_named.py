from typing import Annotated

from aiomcache import Client
from asgikit import Request

from zayt.di import Inject
from zayt.web import get


@get
async def index(request: Request, memcached: Annotated[Client, Inject(name="other")]):
    await memcached.set(b"key", b"value")
    result = (await memcached.get(b"key")).decode("utf-8")

    await request.respond_text(result)
    await memcached.delete(b"key")
