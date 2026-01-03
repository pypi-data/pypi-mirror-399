import copy

import pytest

from zayt.conf.defaults import default_settings
from zayt.conf.settings import Settings
from zayt.ext.error import ExtensionMissingInitFunctionError, ExtensionNotFoundError
from zayt.web.application import Zayt


async def test_non_existent_extension_should_fail():
    settings = Settings(
        copy.copy(default_settings)
        | {
            "__application__": f"{__package__}.application",
            "extensions": ["does.not.exist"],
        }
    )

    app = Zayt(settings)

    with pytest.raises(ExtensionNotFoundError):
        # pylint: disable=protected-access
        await app._lifespan_startup()


async def test_extension_missing_init_function_should_fail():
    settings = Settings(
        copy.copy(default_settings)
        | {
            "__application__": f"{__package__}.application",
            "extensions": [f"{__package__}.extension"],
        }
    )

    app = Zayt(settings)

    with pytest.raises(ExtensionMissingInitFunctionError):
        # pylint: disable=protected-access
        await app._lifespan_startup()
