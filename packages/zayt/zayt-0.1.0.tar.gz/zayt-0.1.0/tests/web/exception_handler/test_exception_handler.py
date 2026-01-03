import copy

from httpx import ASGITransport, AsyncClient

from zayt.conf import Settings
from zayt.conf.defaults import default_settings
from zayt.web.application import Zayt

from .application import DerivedException, MyBaseException, MyException

SETTINGS = Settings(
    default_settings
    | {
        "__application__": f"{__package__}.application",
    }
)


async def test_exception_handler():
    settings = copy.copy(SETTINGS)

    app = Zayt(settings)
    # pylint: disable=protected-access
    await app._lifespan_startup()

    client = AsyncClient(transport=ASGITransport(app=app))
    response = await client.get("http://localhost:8000/")
    assert response.json() == {"exception": MyException.__name__}


async def test_derived_exception_handler():
    settings = copy.copy(SETTINGS)

    app = Zayt(settings)
    # pylint: disable=protected-access
    await app._lifespan_startup()

    client = AsyncClient(transport=ASGITransport(app=app))

    response = await client.get("http://localhost:8000/base")
    assert response.text == f"handler=base; exception={MyBaseException.__name__}"

    response = await client.get("http://localhost:8000/derived")
    assert response.text == f"handler=base; exception={DerivedException.__name__}"
