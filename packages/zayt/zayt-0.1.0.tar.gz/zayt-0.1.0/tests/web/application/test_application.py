from http import HTTPStatus

from httpx import ASGITransport, AsyncClient

from zayt.conf.defaults import default_settings
from zayt.conf.settings import Settings
from zayt.web.application import Zayt


async def test_application():
    settings = Settings(
        default_settings | {"__application__": f"{__package__}.application"}
    )
    app = Zayt(settings)

    client = AsyncClient(transport=ASGITransport(app=app))
    response = await client.get("http://localhost:8000/")
    assert response.text == "Ok"


async def test_not_found():
    settings = Settings(
        default_settings | {"__application__": f"{__package__}.application"}
    )
    app = Zayt(settings)

    client = AsyncClient(transport=ASGITransport(app=app))
    response = await client.get("http://localhost:8000/not-found")
    assert response.status_code == HTTPStatus.NOT_FOUND
