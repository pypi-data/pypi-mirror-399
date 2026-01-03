from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from zayt.web import startup


@startup
async def on_startup(session: AsyncSession):
    await session.scalar(text("select 1"))
