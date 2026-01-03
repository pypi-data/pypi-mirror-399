from typing import Annotated

from asgikit import Request
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from zayt.di import Inject
from zayt.web import get


@get
async def index(request: Request, engine: Annotated[AsyncEngine, Inject(name="other")]):
    async with engine.begin() as conn:
        result = await conn.execute(text("select sqlite_version()"))
        version = result.first()[0]

    await request.respond_text(version)
