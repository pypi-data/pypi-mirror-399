import pytest

from zayt.web.routing.decorator import get
from zayt.web.routing.exception import DuplicateRouteError
from zayt.web.routing.router import Router


def test_duplicate_route_should_raise_error():
    @get
    async def route1(_request, _response):
        pass

    @get
    async def route2(_request, _response):
        pass

    router = Router()

    with pytest.raises(DuplicateRouteError):
        router.route(route1)
        router.route(route2)
