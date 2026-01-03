import json
import os
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


def env(name: str, cast: Callable[[str], T] = str, default: T = None) -> T:
    """Read an environment variable, optionally applying a cast

    :param name: Name of the environment variable
    :param cast: Type to convert the value
        Should be a callable that accepts a ``str`` and returns the converted value.
        :py:type:`bool` receives a special treatment:
        If the value is empty, return ``None``.
        If the value is ``"1"`` or ``"true"`` (ignoring case), the result is ``True``.
        Any other value is ``False``.
        :py:module:`json` also receives a special treatment, in which the value
        is converted with ``json.loads``.
    :param default: Default value if the environment variable is not set
    """

    value = os.environ.get(name)

    if value is None:
        if default is not None:
            return default
        raise ValueError(f"Environment variable '{name}' not set")

    if len(value.strip()) == 0:
        return None

    if cast is bool:
        return _cast_bool(value)

    if cast is json:
        return json.loads(value)

    return cast(value)


def _cast_bool(value: str) -> bool | None:
    """Cast value to bool from str

    :return:
        True if `value.lower()` is "true" or "1"
        None if `value.strip` is empty
        False otherwise
    """

    return value.lower() in {"true", "1"}
