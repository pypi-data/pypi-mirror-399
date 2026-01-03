import os
from http import HTTPStatus
from importlib.util import find_spec

import pytest
from httpx import ASGITransport, AsyncClient

from zayt.conf.defaults import default_settings
from zayt.conf.settings import Settings
from zayt.web.application import Zayt

MEMCACHED_HOST = os.environ.get("MEMCACHED_HOST")


@pytest.mark.skipif(MEMCACHED_HOST is None, reason="MEMCACHED_HOST not defined")
@pytest.mark.skipif(find_spec("aiomcache") is None, reason="aiomcache not present")
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
            "extensions": ["zayt.ext.memcached"],
            "memcached": {database: {"host": MEMCACHED_HOST}},
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
