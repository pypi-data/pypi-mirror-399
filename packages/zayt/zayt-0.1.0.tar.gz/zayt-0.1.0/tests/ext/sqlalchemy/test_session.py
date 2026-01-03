import pytest
from httpx import ASGITransport, AsyncClient

from zayt.conf.defaults import default_settings
from zayt.conf.settings import Settings
from zayt.di.error import ScopedServiceWithoutContextError
from zayt.web.application import Zayt


async def test_application():
    settings = Settings(
        default_settings
        | {
            "__application__": f"{__package__}.application_session",
            "extensions": ["zayt.ext.sqlalchemy"],
            "sqlalchemy": {
                "connections": {"default": {"url": "sqlite+aiosqlite:///:memory:"}}
            },
        }
    )

    app = Zayt(settings)

    # pylint: disable=protected-access
    await app._lifespan_startup()

    client = AsyncClient(transport=ASGITransport(app=app))
    response = await client.get("http://localhost:8000/")

    assert response.text == "1"


async def test_session_outside_request_should_fail():
    settings = Settings(
        default_settings
        | {
            "__application__": f"{__package__}.application_session_startup",
            "extensions": ["zayt.ext.sqlalchemy"],
            "sqlalchemy": {
                "connections": {"default": {"url": "sqlite+aiosqlite:///:memory:"}}
            },
        }
    )

    app = Zayt(settings)

    with pytest.raises(ScopedServiceWithoutContextError):
        # pylint: disable=protected-access
        await app._lifespan_startup()
