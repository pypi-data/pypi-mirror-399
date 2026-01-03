from typing import Annotated

import pytest

from zayt.di.container import Container
from zayt.di.decorator import service
from zayt.di.error import IncompatibleDependencyScopeError
from zayt.di.inject import Inject


@service(scoped=True)
class Service1:
    pass


@service(scoped=False)
class Service2:
    service1: Annotated[Service1, Inject]


@service(scoped=True)
class Service3:
    service2: Annotated[Service2, Inject]


async def test_service_chain_with_mixed_scopes(ioc: Container):
    ioc.register(Service1)
    ioc.register(Service2)
    ioc.register(Service3)

    context = object()

    with pytest.raises(IncompatibleDependencyScopeError):
        await ioc.get(Service3, context=context)
