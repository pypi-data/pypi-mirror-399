from typing import Annotated

from asgikit import Request
from redis.asyncio import Redis

from zayt.di import Inject
from zayt.web import get


@get
async def index(request: Request, redis: Annotated[Redis, Inject(name="other")]):
    await redis.set("key", "value")
    result = (await redis.get("key")).decode("utf-8")

    await request.respond_text(result)
    await redis.delete("key")
