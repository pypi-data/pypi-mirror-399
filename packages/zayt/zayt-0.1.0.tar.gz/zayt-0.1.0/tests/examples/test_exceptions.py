import asyncio
import multiprocessing as mp
from pathlib import Path
from http import HTTPStatus

from httpx import ASGITransport, AsyncClient

from .util import with_app


@with_app
async def _run(app):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://server"
    ) as client:
        response_unauthorized = await client.get("/unauthorized")
        assert response_unauthorized.status_code == HTTPStatus.UNAUTHORIZED

        response_teapot = await client.get("/im-a-teapot")
        assert response_teapot.status_code == HTTPStatus.IM_A_TEAPOT


def run():
    return asyncio.run(_run())


def test_example(monkeypatch):
    path = Path(__file__).parents[2] / "examples" / "exceptions"
    monkeypatch.syspath_prepend(path)
    monkeypatch.chdir(path)

    with mp.Pool(processes=1) as pool:
        pool.apply(run)
