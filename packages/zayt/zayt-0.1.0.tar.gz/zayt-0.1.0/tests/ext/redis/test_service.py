import os
from importlib.util import find_spec
from urllib.parse import urlparse

import pytest

from zayt.conf.defaults import default_settings
from zayt.conf.settings import Settings
from zayt.ext.redis.service import make_service

REDIS_URL = os.getenv("REDIS_URL")

pytestmark = [
    pytest.mark.skipif(REDIS_URL is None, reason="REDIS_URL not defined"),
    pytest.mark.skipif(find_spec("redis") is None, reason="redis not present"),
]

PARSED_URL = urlparse(REDIS_URL) if REDIS_URL else None


async def _test_engine_service(settings: Settings):
    service = make_service("default")(settings)
    async for redis in service:
        result = await redis.ping()
        assert result


async def test_make_service_with_url():
    settings = Settings(
        default_settings
        | {
            "redis": {
                "default": {
                    "url": REDIS_URL,
                },
            },
        }
    )

    await _test_engine_service(settings)


@pytest.mark.skipif(
    PARSED_URL is not None and PARSED_URL.password is None,
    reason="url without password",
)
async def test_make_service_with_url_username_password():
    settings = Settings(
        default_settings
        | {
            "redis": {
                "default": {
                    "url": f"redis://{PARSED_URL.hostname}:{PARSED_URL.port}{PARSED_URL.path}",
                    "username": PARSED_URL.username,
                    "password": PARSED_URL.password,
                },
            },
        }
    )

    await _test_engine_service(settings)


async def test_make_service_with_url_components():
    params = {
        "host": PARSED_URL.hostname,
        "port": PARSED_URL.port,
        "db": int(PARSED_URL.path.strip("/")),
    }

    if (username := PARSED_URL.username) and (password := PARSED_URL.password):
        params |= {
            "username": username,
            "password": password,
        }

    settings = Settings(
        default_settings
        | {
            "redis": {"default": params},
        }
    )

    await _test_engine_service(settings)


async def test_make_service_with_options():
    settings = Settings(
        default_settings
        | {
            "redis": {
                "default": {
                    "url": REDIS_URL,
                    "client_name": "zayt",
                },
            },
        }
    )

    service = make_service("default")(settings)
    async for redis in service:
        connection = await redis.connection_pool.get_connection()
        assert connection.client_name == "zayt"


async def test_make_service_with_retry():
    # pylint: disable=import-outside-toplevel
    # pylint: disable=import-outside-toplevel
    from redis.backoff import ConstantBackoff
    from redis.retry import Retry

    settings = Settings(
        default_settings
        | {
            "redis": {
                "default": {
                    "url": REDIS_URL,
                    "retry": Retry(retries=1, backoff=ConstantBackoff(1.0)),
                },
            },
        }
    )

    service = make_service("default")(settings)
    async for redis in service:
        connection = await redis.connection_pool.get_connection()
        assert connection.retry is not None
