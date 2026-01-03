import copy
from http import HTTPStatus
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from zayt.conf import Settings
from zayt.conf.defaults import default_settings
from zayt.web.application import Zayt
from zayt.web.middleware.files import static_files_middleware

MIDDLEWARE = [
    f"{static_files_middleware.__module__}:{static_files_middleware.__name__}"
]


@pytest.fixture(autouse=True)
def chdir_fixture(monkeypatch):
    monkeypatch.chdir(Path(__file__).parent)


async def test_static_file():
    settings = Settings(
        default_settings
        | {
            "__application__": f"{__package__}.application",
            "asgi_middleware": copy.copy(MIDDLEWARE),
        }
    )
    app = Zayt(settings)
    # pylint: disable=protected-access
    await app._lifespan_startup()

    client = AsyncClient(transport=ASGITransport(app=app))
    response = await client.get("http://localhost:8000/static/lorem-ipsum.txt")

    assert response.status_code == HTTPStatus.OK
    assert "text/plain" in response.headers["content-type"]
    assert response.text == "Lorem ipsum dolor sit amet."


async def test_static_file_mapping():
    settings = Settings(
        default_settings
        | {
            "__application__": f"{__package__}.application",
            "asgi_middleware": copy.copy(MIDDLEWARE),
            "staticfiles": default_settings["staticfiles"]
            | {
                "mappings": {
                    "text-file": "lorem-ipsum.txt",
                },
            },
        }
    )
    app = Zayt(settings)
    # pylint: disable=protected-access
    await app._lifespan_startup()

    client = AsyncClient(transport=ASGITransport(app=app))
    response = await client.get("http://localhost:8000/text-file")

    assert response.request.url.path == "/text-file"
    assert response.status_code == HTTPStatus.OK
    assert "text/plain" in response.headers["Content-Type"]
    assert response.text == "Lorem ipsum dolor sit amet."


async def test_static_files_path():
    settings = Settings(
        default_settings
        | {
            "__application__": f"{__package__}.application",
            "asgi_middleware": copy.copy(MIDDLEWARE),
            "staticfiles": default_settings["staticfiles"]
            | {
                "path": "assets",
            },
        }
    )
    app = Zayt(settings)
    # pylint: disable=protected-access
    await app._lifespan_startup()

    client = AsyncClient(transport=ASGITransport(app=app))
    response = await client.get("http://localhost:8000/static/lorem-ipsum.txt")
    assert response.status_code == HTTPStatus.NOT_FOUND

    response = await client.get("http://localhost:8000/assets/lorem-ipsum.txt")
    assert response.status_code == HTTPStatus.OK
    assert "text/plain" in response.headers["Content-Type"]
    assert response.text == "Lorem ipsum dolor sit amet."


async def test_static_files_root():
    settings = Settings(
        default_settings
        | {
            "__application__": f"{__package__}.application",
            "asgi_middleware": copy.copy(MIDDLEWARE),
            "staticfiles": default_settings["staticfiles"]
            | {
                "root": Path(__file__).parent / "resources" / "assets",
            },
        }
    )
    app = Zayt(settings)
    # pylint: disable=protected-access
    await app._lifespan_startup()

    client = AsyncClient(transport=ASGITransport(app=app))
    response = await client.get("http://localhost:8000/static/style.css")
    assert response.status_code == HTTPStatus.OK
    assert "text/css" in response.headers["Content-Type"]
    assert response.text == "body { display: none }"
