import asyncio
from importlib.util import find_spec
import multiprocessing as mp
import os
from pathlib import Path

from httpx import ASGITransport, AsyncClient
import pytest

from .util import with_app


@with_app
async def _run(app):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://server"
    ) as client:
        for i in range(1, 4):
            response = await client.get("/")
            assert response.json() == {"number": i}


def run():
    return asyncio.run(_run())


REDIS_URL = os.environ.get("REDIS_URL")


@pytest.mark.skipif(REDIS_URL is None, reason="REDIS_URL not set")
@pytest.mark.skipif(find_spec("redis") is None, reason="redis not present")
def test_example(monkeypatch):
    path = Path(__file__).parents[2] / "examples" / "redis"
    monkeypatch.syspath_prepend(path)
    monkeypatch.chdir(path)

    with mp.Pool(processes=1) as pool:
        pool.apply(run)
