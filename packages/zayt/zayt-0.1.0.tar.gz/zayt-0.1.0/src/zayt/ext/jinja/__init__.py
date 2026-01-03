from importlib.util import find_spec

from zayt.conf.settings import Settings
from zayt.di.container import Container
from zayt.ext.jinja.service import JinjaTemplate, jinja_environment


async def init_extension(container: Container, _settings: Settings):
    if find_spec("jinja2") is None:
        raise ModuleNotFoundError(
            "Missing 'jinja2'. Install 'zayt' with 'jinja' extra."
        )

    container.register(jinja_environment)
    container.register(JinjaTemplate)
