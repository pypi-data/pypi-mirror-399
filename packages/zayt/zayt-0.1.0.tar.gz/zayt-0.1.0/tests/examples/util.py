import inspect

from zayt.conf.settings import get_settings
from zayt.web.application import Zayt


def with_app(target):
    assert inspect.iscoroutinefunction(target)

    async def inner(*args, **kwargs):
        app = Zayt(get_settings())
        await app._lifespan_startup()

        try:
            await target(app, *args, **kwargs)
        finally:
            await app._lifespan_shutdown()

    return inner
