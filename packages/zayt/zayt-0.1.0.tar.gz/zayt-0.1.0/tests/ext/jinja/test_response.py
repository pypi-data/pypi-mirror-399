from pathlib import Path

from httpx import ASGITransport, AsyncClient

from zayt.conf.defaults import default_settings
from zayt.conf.settings import Settings
from zayt.web.application import Zayt

PATH = str((Path(__file__).parent / "templates").absolute())

settings = Settings(
    default_settings
    | {
        "__application__": f"{__package__}.application",
        "extensions": ["zayt.ext.jinja"],
        "jinja": {"loader": {"searchpath": [PATH]}},
    }
)


async def test_render():
    app = Zayt(settings)
    # pylint: disable=protected-access
    await app._lifespan_startup()

    client = AsyncClient(transport=ASGITransport(app=app))
    response = await client.get("http://localhost:8000/render")

    assert response.status_code == 200
    assert response.text == "Jinja"
    assert response.headers["Content-Length"] == str(len("Jinja"))
    assert "text/html" in response.headers["Content-Type"]


async def test_stream():
    app = Zayt(settings)
    # pylint: disable=protected-access
    await app._lifespan_startup()

    client = AsyncClient(transport=ASGITransport(app=app))
    response = await client.get("http://localhost:8000/stream")

    assert response.status_code == 200
    assert response.text == "Jinja"
    assert "Content-Length" not in response.headers


async def test_content_type():
    app = Zayt(settings)
    # pylint: disable=protected-access
    await app._lifespan_startup()

    client = AsyncClient(transport=ASGITransport(app=app))
    response = await client.get("http://localhost:8000/content_type")

    assert response.status_code == 200
    assert response.text == "Jinja"
    assert response.headers["Content-Length"] == str(len("Jinja"))
    assert "text/plain" in response.headers["Content-Type"]
