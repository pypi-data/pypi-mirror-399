import asyncio
import multiprocessing as mp
from pathlib import Path

from httpx import ASGITransport, AsyncClient

from .util import with_app


@with_app
async def _run(app):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://server"
    ) as client:
        response = await client.get("/")
        assert response.status_code == 200
        assert (
            '<img src="/static/python-powered.png" alt="python powered" />'
            in response.text
        )

        response = await client.get("/favicon.ico")
        assert response.headers.get("content-type") == "image/x-icon"

        response = await client.get("/static/python-powered.png")
        assert response.headers.get("content-type") == "image/png"


def run():
    return asyncio.run(_run())


def test_example(monkeypatch):
    path = Path(__file__).parents[2] / "examples" / "middleware_files"
    monkeypatch.syspath_prepend(path)
    monkeypatch.chdir(path)

    with mp.Pool(processes=1) as pool:
        pool.apply(run)
