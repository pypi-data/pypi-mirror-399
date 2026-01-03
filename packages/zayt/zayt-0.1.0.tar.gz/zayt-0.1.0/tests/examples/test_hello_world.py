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
        response = await client.get("/", params={"name": "Python", "number": 3})
        assert response.json() == {"greeting": "Hello, Python!", "number": 3}

        response = await client.get("/Asgi")
        assert response.json() == {"greeting": "Hello, Asgi!"}

        response = await client.post("/", json={"greeting": "Hello, World!"})
        assert response.json() == {"result": {"greeting": "Hello, World!"}}

        for path in ["/multiple", "/annotations"]:
            response = await client.get(path)
            assert response.json() == {"path": path}


def run():
    return asyncio.run(_run())


def test_example(monkeypatch):
    path = Path(__file__).parents[2] / "examples" / "hello_world"
    monkeypatch.syspath_prepend(path)
    monkeypatch.chdir(path)

    with mp.Pool(processes=1) as pool:
        pool.apply(run)
