from zayt.conf.defaults import default_settings
from zayt.conf.settings import Settings
from zayt.web.application import Zayt
from zayt.web.lifecycle.decorator import startup


@startup
def on_startup():
    print("startup", end="")


async def test_application(capfd):
    settings = Settings(
        default_settings
        | {
            "__application__": f"{test_application.__module__}",
        }
    )

    app = Zayt(settings)

    # pylint: disable=protected-access
    await app._lifespan_startup()
    assert capfd.readouterr().out == "startup"
