import copy
from http import HTTPStatus
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from zayt.conf import Settings
from zayt.conf.defaults import default_settings
from zayt.web.application import Zayt
from zayt.web.middleware.files import uploaded_files_middleware

MIDDLEWARE = [
    f"{uploaded_files_middleware.__module__}:{uploaded_files_middleware.__name__}"
]


@pytest.fixture(autouse=True)
def chdir_fixture(monkeypatch):
    monkeypatch.chdir(Path(__file__).parent)


async def test_uploaded_file():
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
    response = await client.get("http://localhost:8000/uploads/lorem-ipsum.txt")

    assert response.status_code == HTTPStatus.OK
    assert "text/plain" in response.headers["Content-Type"]
    assert response.text == "Lorem ipsum dolor sit amet."


async def test_uploaded_files_path():
    settings = Settings(
        default_settings
        | {
            "__application__": f"{__package__}.application",
            "asgi_middleware": copy.copy(MIDDLEWARE),
            "uploadedfiles": default_settings["uploadedfiles"]
            | {
                "path": "media",
            },
        }
    )
    app = Zayt(settings)
    # pylint: disable=protected-access
    await app._lifespan_startup()

    client = AsyncClient(transport=ASGITransport(app=app))
    response = await client.get("http://localhost:8000/uploads/lorem-ipsum.txt")
    assert response.status_code == HTTPStatus.NOT_FOUND

    response = await client.get("http://localhost:8000/media/lorem-ipsum.txt")
    assert response.status_code == HTTPStatus.OK
    assert "text/plain" in response.headers["Content-Type"]
    assert response.text == "Lorem ipsum dolor sit amet."


async def test_uploaded_files_root():
    settings = Settings(
        default_settings
        | {
            "__application__": f"{__package__}.application",
            "asgi_middleware": copy.copy(MIDDLEWARE),
            "uploadedfiles": default_settings["uploadedfiles"]
            | {
                "root": Path(__file__).parent / "resources" / "media",
            },
        }
    )
    app = Zayt(settings)
    # pylint: disable=protected-access
    await app._lifespan_startup()

    client = AsyncClient(transport=ASGITransport(app=app))
    response = await client.get("http://localhost:8000/uploads/data.json")
    assert response.status_code == HTTPStatus.OK
    assert "application/json" in response.headers["Content-Type"]
    assert response.text == '{"message": "lorem ipsum"}'
