from typing import Annotated

from asgikit import Request
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from zayt.di import Inject, service
from zayt.web import get


@service(scoped=True)
class MyService:
    session: Annotated[AsyncSession, Inject]

    async def select(self):
        return await self.session.scalar(text("select 1"))


@get
async def index(request: Request, my_service: MyService):
    value = await my_service.select()
    await request.respond_text(str(value))
