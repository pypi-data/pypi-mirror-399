import asyncio
import multiprocessing as mp
from pathlib import Path

from httpx import AsyncClient
from httpx_ws import aconnect_ws
from httpx_ws.transport import ASGIWebSocketTransport

from .util import with_app


@with_app
async def _run(app):
    async with AsyncClient(
        transport=ASGIWebSocketTransport(app), base_url="http://server"
    ) as client:
        response = await client.get("")
        assert response.status_code == 200
        assert 'new WebSocket("ws://localhost:8000/chat");' in response.text

        async with aconnect_ws("/chat", client) as ws:
            await ws.send_text("Hello World!")
            message = await ws.receive_text()
            assert message == "Hello World!"


def run():
    return asyncio.run(_run())


def test_example(monkeypatch):
    path = Path(__file__).parents[2] / "examples" / "websocket"
    monkeypatch.syspath_prepend(path)
    monkeypatch.chdir(path)

    with mp.Pool(processes=1) as pool:
        pool.apply(run)
