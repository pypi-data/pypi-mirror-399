import pytest

from zayt.di.container import Container


@pytest.fixture
async def ioc() -> Container:
    return Container()
