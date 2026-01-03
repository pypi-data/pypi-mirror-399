import json

import pytest

from zayt.conf import env


def test_str(monkeypatch):
    monkeypatch.setenv("TEST", "value")
    result = env("TEST")
    assert result == "value"


@pytest.mark.parametrize(
    "value, typecast, expected",
    [
        ("1", int, 1),
        ("1.2", float, 1.2),
        ("true", bool, True),
        ("1", bool, True),
        ("false", bool, False),
        ("0", bool, False),
        ("any", bool, False),
        ('{"key": "value"}', json, {"key": "value"}),
        ("", int, None),
        ("", float, None),
        ("", str, None),
        ("", bool, None),
    ],
)
def test_cast(value, typecast, expected, monkeypatch):
    monkeypatch.setenv("TEST", value)
    result = env("TEST", cast=typecast)
    assert result == expected


def test_cast_function(monkeypatch):
    monkeypatch.setenv("TEST", "value")

    def cast_func(value: str):
        return [value]

    result = env("TEST", cast=cast_func)
    assert result == ["value"]


def test_cast_class_init(monkeypatch):
    monkeypatch.setenv("TEST", "value")

    class MyType:
        def __init__(self, value):
            self.value = value

    result = env("TEST", cast=MyType)
    assert isinstance(result, MyType)


def test_default():
    result = env("TEST", default="default")
    assert result == "default"


def test_missing_variable_should_fail():
    with pytest.raises(ValueError, match="Environment variable 'TEST' not set"):
        env("TEST")
