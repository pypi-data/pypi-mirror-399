from typing import Annotated

import pytest

from zayt.di.container import Container
from zayt.di.decorator import service
from zayt.di.error import (
    IncompatibleDependencyScopeError,
    ScopedServiceWithoutContextError,
)
from zayt.di.inject import Inject


async def test_service_with_different_scope(ioc: Container):
    @service
    class ApplicationScopedService:
        pass

    @service(scoped=True)
    class ContextScopedService:
        dependency: Annotated[ApplicationScopedService, Inject]

    ioc.register(ApplicationScopedService)
    ioc.register(ContextScopedService)

    context = object()

    result = await ioc.get(ContextScopedService, context=context)
    assert isinstance(result.dependency, ApplicationScopedService)


async def test_get_context_scoped_service_witout_context_should_fail(ioc: Container):
    @service(scoped=True)
    class ContextScopedService:
        pass

    ioc.register(ContextScopedService)

    with pytest.raises(ScopedServiceWithoutContextError):
        await ioc.get(ContextScopedService)


async def test_service_with_incompatible_scoped_dependency_should_fail(ioc: Container):
    @service(scoped=True)
    class ContextScopedService:
        pass

    @service
    class ApplicationScopedService:
        dependency: Annotated[ContextScopedService, Inject]

    ioc.register(ContextScopedService)
    ioc.register(ApplicationScopedService)

    with pytest.raises(IncompatibleDependencyScopeError):
        await ioc.get(ApplicationScopedService)
