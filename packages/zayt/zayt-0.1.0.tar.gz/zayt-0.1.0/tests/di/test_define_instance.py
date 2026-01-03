from zayt.di.container import Container
from zayt.di.decorator import service


@service
class Service:
    pass


async def test_define_service_not_registered(ioc: Container):
    instance = Service()
    ioc.define(Service, instance)

    result = await ioc.get(Service)

    assert result is instance


async def test_define_service_already_registered(ioc: Container):
    ioc.register(Service)
    instance = Service()
    ioc.define(Service, instance)

    result = await ioc.get(Service)

    assert result is instance
