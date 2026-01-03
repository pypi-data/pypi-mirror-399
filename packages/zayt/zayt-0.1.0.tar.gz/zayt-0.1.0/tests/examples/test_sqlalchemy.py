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
        response = await client.get("/")
        result = response.json().get("model")
        assert result is not None
        assert result["name"] == "MyModel"

        response = await client.get("/other")
        result = response.json().get("model")
        assert result is not None
        assert result["name"] == "OtherModel"


def run():
    return asyncio.run(_run())


POSTGRES_URL = os.getenv("POSTGRES_URL")


@pytest.mark.skipif(POSTGRES_URL is None, reason="POSTGRES_URL not defined")
@pytest.mark.skipif(find_spec("asyncpg") is None, reason="asyncpg not present")
def test_example(monkeypatch):
    path = Path(__file__).parents[2] / "examples" / "sqlalchemy"
    monkeypatch.syspath_prepend(path)
    monkeypatch.chdir(path)

    with mp.Pool(processes=1) as pool:
        pool.apply(run)
