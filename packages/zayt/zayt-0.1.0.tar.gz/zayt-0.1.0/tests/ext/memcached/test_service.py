import os
from importlib.util import find_spec

import pytest

from zayt.conf import Settings
from zayt.conf.defaults import default_settings
from zayt.ext.memcached.service import make_service

MEMCACHED_HOST = os.getenv("MEMCACHED_HOST")

pytestmark = [
    pytest.mark.skipif(MEMCACHED_HOST is None, reason="MEMCACHED_HOST not defined"),
    pytest.mark.skipif(find_spec("aiomcache") is None, reason="aiomcache not present"),
]


async def _test_make_service(settings: Settings):
    service = make_service("default")(settings)
    async for memcached in service:
        await memcached.set(b"test", b"test")
        result = await memcached.get(b"test")
        assert result == b"test"
        await memcached.delete(b"test")


async def test_make_service_with_address():
    settings = Settings(
        default_settings
        | {
            "memcached": {
                "default": {
                    "host": MEMCACHED_HOST,
                },
            },
        }
    )

    await _test_make_service(settings)


async def test_make_service_with_options():
    settings = Settings(
        default_settings
        | {
            "memcached": {
                "default": {
                    "host": MEMCACHED_HOST,
                    "pool_size": 10,
                    "pool_minsize": 1,
                },
            },
        }
    )

    service = make_service("default")(settings)
    async for memcached in service:
        # pylint: disable=protected-access
        assert memcached._pool._maxsize == 10
        # pylint: disable=protected-access
        assert memcached._pool._minsize == 1
