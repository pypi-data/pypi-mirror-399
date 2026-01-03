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

        response = await client.get("/protected")
        assert response.status_code == 401

        response = await client.get("/protected", auth=("admin", "123"))
        assert response.status_code == 200

        response = await client.get("/logout")
        assert response.status_code == 401
        assert response.headers["WWW-Authenticate"] == 'Basic realm="localhost:8000"'


def run():
    return asyncio.run(_run())


def test_example(monkeypatch):
    path = Path(__file__).parents[2] / "examples" / "middleware"
    monkeypatch.syspath_prepend(path)
    monkeypatch.chdir(path)

    with mp.Pool(processes=1) as pool:
        pool.apply(run)
