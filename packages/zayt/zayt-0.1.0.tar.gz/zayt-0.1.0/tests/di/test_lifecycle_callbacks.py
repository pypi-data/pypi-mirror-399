from typing import Annotated

import pytest

from zayt.di.container import Container
from zayt.di.decorator import service
from zayt.di.inject import Inject


@service
class ServiceInitialize:
    def initialize(self):
        pass


@service
class ServiceAsyncInitialize:
    async def initialize(self):
        pass


class Service:
    def finalization_method(self):
        pass


@service
class ServiceFinalize:
    def finalize(self):
        pass


@service
class ServiceAsyncFinalize:
    async def finalize(self):
        pass


@service
def factory_finalize() -> Service:
    instance = Service()
    yield instance
    instance.finalization_method()


@service
async def factory_async_finalize() -> Service:
    instance = Service()
    yield instance
    instance.finalization_method()


@service
class FinalizerOrder1:
    def initialize(self):
        pass

    def finalize(self):
        pass


@service
class FinalizerOrder2:
    dep: Annotated[FinalizerOrder1, Inject]

    def initialize(self):
        pass

    def finalize(self):
        pass


@service(scoped=True)
class ContextScopeFinalize:
    async def finalize(self):
        pass


@pytest.mark.parametrize("service_class", [ServiceInitialize, ServiceAsyncInitialize])
async def test_call_initialize(ioc: Container, mocker, service_class):
    initializer = mocker.patch.object(service_class, "initialize")
    ioc.register(service_class)

    await ioc.get(service_class)
    initializer.assert_called_once()


@pytest.mark.parametrize("service_class", [ServiceFinalize, ServiceAsyncFinalize])
async def test_call_finalize(ioc: Container, mocker, service_class):
    finalizer = mocker.patch.object(service_class, "finalize")
    ioc.register(service_class)

    await ioc.get(service_class)
    await ioc.finalize()

    finalizer.assert_called_once()


@pytest.mark.parametrize("factory", [factory_finalize, factory_async_finalize])
async def test_call_factory_finalize(ioc: Container, mocker, factory):
    finalizer = mocker.patch.object(Service, "finalization_method")
    ioc.register(factory)

    await ioc.get(Service)
    await ioc.finalize()

    finalizer.assert_called_once()


async def test_finalizer_order(ioc: Container, mocker):
    output = []

    def new_method(self):
        output.append(self.__class__.__name__)

    mocker.patch.object(FinalizerOrder1, "initialize", new_method)
    mocker.patch.object(FinalizerOrder2, "initialize", new_method)
    mocker.patch.object(FinalizerOrder1, "finalize", new_method)
    mocker.patch.object(FinalizerOrder2, "finalize", new_method)

    ioc.register(FinalizerOrder1)
    ioc.register(FinalizerOrder2)

    await ioc.get(FinalizerOrder2)
    await ioc.finalize()

    expected = [
        "FinalizerOrder1",
        "FinalizerOrder2",
        "FinalizerOrder2",
        "FinalizerOrder1",
    ]
    assert output == expected


async def test_context_finalizer_is_called(ioc: Container, mocker):
    service_finalize_func = mocker.patch.object(ServiceFinalize, "finalize")
    context_scope_finalize_func = mocker.patch.object(ContextScopeFinalize, "finalize")

    ioc.register(ServiceFinalize)
    ioc.register(ContextScopeFinalize)

    context = object()

    await ioc.get(ServiceFinalize, context=context)
    await ioc.get(ContextScopeFinalize, context=context)

    await ioc.finalize(context)

    service_finalize_func.assert_not_called()
    context_scope_finalize_func.assert_called_once()

    await ioc.finalize()
    service_finalize_func.assert_called_once()


async def test_all_finalizers_called(ioc: Container, mocker):
    service_finalize_func = mocker.patch.object(ServiceFinalize, "finalize")
    context_scope_finalize_func = mocker.patch.object(ContextScopeFinalize, "finalize")

    ioc.register(ServiceFinalize)
    ioc.register(ContextScopeFinalize)

    context = object()

    await ioc.get(ServiceFinalize)
    await ioc.get(ContextScopeFinalize, context=context)

    await ioc.finalize()
    service_finalize_func.assert_called_once()
    context_scope_finalize_func.assert_called_once()
