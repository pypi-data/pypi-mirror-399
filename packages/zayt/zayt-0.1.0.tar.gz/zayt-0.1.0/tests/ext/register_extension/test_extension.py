from zayt.conf.defaults import default_settings
from zayt.conf.settings import Settings
from zayt.web.application import Zayt


async def test_extension():
    settings = Settings(
        default_settings
        | {
            "__application__": "tests.ext.register_extension.application",
            "extensions": ["tests.ext.register_extension.extension"],
        }
    )

    app = Zayt(settings)

    # pylint: disable=protected-access
    await app._lifespan_startup()

    assert settings.tested
