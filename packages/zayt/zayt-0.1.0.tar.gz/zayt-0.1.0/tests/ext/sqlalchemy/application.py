from asgikit import Request
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker

from zayt.web import get


@get
async def index(request: Request, sessionmaker: async_sessionmaker):
    async with sessionmaker() as session:
        result = await session.execute(text("select sqlite_version()"))
        version = result.first()[0]

    await request.respond_json(version)
