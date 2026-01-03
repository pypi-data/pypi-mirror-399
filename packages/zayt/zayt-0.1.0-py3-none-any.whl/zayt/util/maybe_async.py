import inspect
from collections.abc import Awaitable, Callable
from typing import Any, ParamSpec

from asgikit.sync import run_sync

P = ParamSpec("P")


async def call_maybe_async(
    target: Awaitable | Callable[P, Any], /, *args: P.args, **kwargs: P.kwargs
) -> Any:
    if inspect.isawaitable(target):
        return await target

    if not callable(target):
        raise TypeError(f"{repr(target)} is not callable")

    call = target if inspect.isroutine(target) else getattr(target, "__call__")

    if inspect.iscoroutinefunction(call):
        return await call(*args, **kwargs)

    return await run_sync(call, *args, **kwargs)
