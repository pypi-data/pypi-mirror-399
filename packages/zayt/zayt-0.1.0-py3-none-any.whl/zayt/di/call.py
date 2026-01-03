from collections.abc import Callable
from typing import Any

from zayt.util.maybe_async import call_maybe_async
from zayt.di.container import Container
from zayt.di.service.parse import get_dependencies


async def call_with_dependencies(
    di: Container,
    target: Callable,
    *,
    args: list | tuple = None,
    context: Any = None,
):
    args = args or []

    dependencies = {
        name: await di.get(
            dep.service, name=dep.name, optional=dep.optional, context=context
        )
        for name, dep in get_dependencies(target, skip=len(args))
    }

    return await call_maybe_async(target, *args, **dependencies)
