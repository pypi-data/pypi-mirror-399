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
        assert "Click Me" in response.text

        for i in range(1, 4):
            response = await client.post("/clicked")
            assert f">{i}<" in response.text


def run():
    return asyncio.run(_run())


def test_example(monkeypatch):
    path = Path(__file__).parents[2] / "examples" / "htmx"
    monkeypatch.syspath_prepend(path)
    monkeypatch.chdir(path)

    with mp.Pool(processes=1) as pool:
        pool.apply(run)
