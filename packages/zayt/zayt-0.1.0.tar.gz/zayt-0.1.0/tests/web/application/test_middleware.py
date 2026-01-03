from httpx import ASGITransport, AsyncClient

from zayt.conf import Settings
from zayt.conf.defaults import default_settings
from zayt.di.decorator import service
from zayt.web.application import Zayt


def my_middleware(app):
    async def inner(scope, receive, send):
        async def new_send(event: dict):
            if event["type"] == "http.response.body":
                event["body"] = b"Middleware Ok"
            await send(event)

        await app(scope, receive, new_send)

    return inner


class MyService:
    pass


def my_middleware_with_dep(app, dep: MyService):
    async def inner(scope, receive, send):
        async def new_send(event: dict):
            if event["type"] == "http.response.body":
                event["body"] = f"Middleware Ok ({dep.__class__.__name__})".encode()
            await send(event)

        await app(scope, receive, new_send)

    return inner


async def test_middleware():
    settings = Settings(
        default_settings
        | {
            "__application__": f"{__package__}.application",
            "asgi_middleware": [f"{__package__}.test_middleware:my_middleware"],
        }
    )
    app = Zayt(settings)
    # pylint: disable=protected-access
    await app._lifespan_startup()

    client = AsyncClient(transport=ASGITransport(app=app))
    response = await client.get("http://localhost:8000/")
    assert response.text == "Middleware Ok"


async def test_middleware_with_dep():
    settings = Settings(
        default_settings
        | {
            "__application__": f"{__package__}.application",
            "asgi_middleware": [f"{__package__}.test_middleware:my_middleware_with_dep"],
        }
    )
    app = Zayt(settings)
    app.di.register(service(MyService))
    # pylint: disable=protected-access
    await app._lifespan_startup()

    client = AsyncClient(transport=ASGITransport(app=app))
    response = await client.get("http://localhost:8000/")
    assert response.text == f"Middleware Ok ({MyService.__name__})"
