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
        assert "<title>Zayt</title>" in response.text
        assert "<h1>Heading</h1>" in response.text


def run():
    return asyncio.run(_run())


def test_example(monkeypatch):
    path = Path(__file__).parents[2] / "examples" / "jinja"
    monkeypatch.syspath_prepend(path)
    monkeypatch.chdir(path)

    with mp.Pool(processes=1) as pool:
        pool.apply(run)
