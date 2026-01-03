import os
from importlib.util import find_spec
from http import HTTPStatus

import pytest
from httpx import ASGITransport, AsyncClient

from zayt.conf.defaults import default_settings
from zayt.conf.settings import Settings
from zayt.web.application import Zayt

REDIS_URL = os.environ.get("REDIS_URL")


@pytest.mark.skipif(REDIS_URL is None, reason="REDIS_URL not set")
@pytest.mark.skipif(find_spec("redis") is None, reason="redis not present")
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
            "extensions": ["zayt.ext.redis"],
            "redis": {database: {"url": REDIS_URL}},
        }
    )

    app = Zayt(settings)

    # pylint: disable=protected-access
    await app._lifespan_startup()

    client = AsyncClient(transport=ASGITransport(app=app))
    response = await client.get("http://localhost:8000/")

    # pylint: disable=protected-access
    await app._lifespan_shutdown()

    assert response.status_code == HTTPStatus.OK
