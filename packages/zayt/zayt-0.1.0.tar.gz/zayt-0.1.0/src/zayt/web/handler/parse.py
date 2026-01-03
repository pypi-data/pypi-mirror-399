import inspect
import typing
from collections.abc import Callable
from functools import cache
from typing import Annotated

from zayt.di.inject import Inject
from zayt.web.handler.model import RequestParam
from zayt.web.routing.exception import HandlerUntypedParametersError


def assert_params_annotated(handler: Callable, *, skip: int):
    """Asserts that parameters past 'skip' are annotated.

    :raises HandlerUntypedParametersError: if parameters are not annotated.
    """
    signature = inspect.signature(handler)
    parameters = list(signature.parameters.values())

    if untyped_params := [
        p.name for p in parameters[skip:] if p.annotation is inspect.Signature.empty
    ]:
        raise HandlerUntypedParametersError(handler, untyped_params)


@cache
def parse_handler_params(
    handler: Callable, *, skip: int
) -> list[tuple[str, RequestParam]]:
    """parse handler parameters from function signature

    returns: list of 2-tuples of parameter name and parameter specification
    :raises HandlerUntypedParametersError:
    """

    assert_params_annotated(handler, skip=skip)

    result = []

    signature = inspect.signature(handler, eval_str=True)
    parameters = list(signature.parameters.keys())

    if len(parameters) == 0:
        return result

    if len(parameters) <= skip:
        return result

    for name in parameters[skip:]:  # skip request parameter
        type_hint = signature.parameters[name].annotation
        has_default = signature.parameters[name].default is not inspect.Parameter.empty

        if typing.get_origin(type_hint) is not Annotated:
            result.append((name, RequestParam(type_hint, None, has_default)))
        else:
            # Annotated is garanteed to have at least 2 args
            param_type, param_meta, *_ = typing.get_args(type_hint)
            if not (param_meta is Inject or isinstance(param_meta, Inject)):
                raise TypeError("Inject")
            result.append((name, RequestParam(param_type, param_meta, has_default)))

    return result
