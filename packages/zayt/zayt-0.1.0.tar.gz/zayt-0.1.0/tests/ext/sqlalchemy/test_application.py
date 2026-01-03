from http import HTTPStatus

import pytest
from httpx import ASGITransport, AsyncClient

from zayt.conf.defaults import default_settings
from zayt.conf.settings import Settings
from zayt.web.application import Zayt


@pytest.mark.parametrize(
    "application,database",
    [
        ("application", "default"),
        ("application_named", "other"),
    ],
    ids=["default", "named"],
)
async def test_application(application: str, database: str):
    settings = Settings(
        default_settings
        | {
            "__application__": f"{__package__}.{application}",
            "extensions": ["zayt.ext.sqlalchemy"],
            "sqlalchemy": {
                "connections": {database: {"url": "sqlite+aiosqlite:///:memory:"}}
            },
        }
    )

    app = Zayt(settings)

    # pylint: disable=protected-access
    await app._lifespan_startup()

    client = AsyncClient(transport=ASGITransport(app=app))
    response = await client.get("http://localhost:8000/")

    assert response.status_code == HTTPStatus.OK, response.text
