from httpx import AsyncClient
from httpx_ws import aconnect_ws, WebSocketDisconnect
from httpx_ws.transport import ASGIWebSocketTransport, UnhandledWebSocketEvent

import pytest

from zayt.conf.defaults import default_settings
from zayt.conf.settings import Settings
from zayt.web.application import Zayt


@pytest.mark.skip
async def test_websocket_not_found():
    settings = Settings(
        default_settings | {"__application__": __package__ + ".application"}
    )
    app = Zayt(settings)

    async with AsyncClient(transport=ASGIWebSocketTransport(app)) as client:
        with pytest.raises(WebSocketDisconnect):
            await aconnect_ws("http://localhost", client).__aenter__()


@pytest.mark.skip
async def test_websocket_new_raising_error(caplog):
    settings = Settings(
        default_settings | {"__application__": __package__ + ".application"}
    )
    app = Zayt(settings)

    async with AsyncClient(transport=ASGIWebSocketTransport(app)) as client:
        with pytest.raises(WebSocketDisconnect, match="1011"):
            await aconnect_ws("http://localhost/exception/new", client).__aenter__()


@pytest.mark.skip
async def test_websocket_accepted_raising_error():
    settings = Settings(
        default_settings | {"__application__": __package__ + ".application"}
    )
    app = Zayt(settings)

    async with AsyncClient(transport=ASGIWebSocketTransport(app)) as client:
        with pytest.raises(UnhandledWebSocketEvent):
            async with aconnect_ws("http://localhost/exception/accepted", client) as ws:
                await ws.ping()
