import pytest

from zayt.di.container import Container
from zayt.di.decorator import service
from zayt.di.error import FactoryMissingReturnTypeError


class Service1:
    pass


@service
async def service1_factory() -> Service1:
    yield Service1()
    print("Service1")


class Service2:
    def __init__(self, service1: Service1):
        self.service1 = service1


@service
async def service2_factory(service1: Service1) -> Service2:
    yield Service2(service1)
    print("Service2")


class Interface:
    pass


class Implementation(Interface):
    pass


@service(provides=Interface)
async def interface_factory() -> Interface:
    yield Implementation()
    print("Interface Implementation")


def test_has_service(ioc: Container):
    ioc.register(service1_factory)
    assert ioc.has(Service1)


async def test_service_with_provided_interface(ioc: Container, capfd):
    ioc.register(interface_factory)

    instance = await ioc.get(Interface)
    assert isinstance(instance, Implementation)

    await ioc.finalize()
    assert capfd.readouterr().out == "Interface Implementation\n"


async def test_inject_singleton(ioc: Container, capfd):
    ioc.register(service1_factory)
    ioc.register(service2_factory)

    instance = await ioc.get(Service2)
    assert isinstance(instance, Service2)
    assert isinstance(instance.service1, Service1)

    other_instance = await ioc.get(Service2)
    assert other_instance is instance
    assert other_instance.service1 is instance.service1

    await ioc.finalize()
    assert capfd.readouterr().out == "Service2\nService1\n"


async def test_interface_implementation(ioc: Container, capfd):
    ioc.register(interface_factory)

    instance = await ioc.get(Interface)
    assert isinstance(instance, Implementation)

    await ioc.finalize()
    assert capfd.readouterr().out == "Interface Implementation\n"


def test_factory_function_without_return_type_should_fail(ioc: Container):
    @service
    async def service_factory():
        pass

    with pytest.raises(FactoryMissingReturnTypeError):
        ioc.register(service_factory)


def test_provides_option_should_log_warning(ioc: Container, log_output):
    ioc.register(interface_factory)

    assert (
        log_output.entries[0]["event"]
        == "option 'provides' on a factory function has no effect"
    )
    assert (
        log_output.entries[0]["service"]
        == "tests.di.test_service_generator_async.interface_factory"
    )
