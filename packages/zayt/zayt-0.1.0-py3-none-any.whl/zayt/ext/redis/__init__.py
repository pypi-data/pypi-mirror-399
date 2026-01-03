from importlib.util import find_spec

from zayt.conf.settings import Settings
from zayt.di.container import Container

from .service import make_service


def init_extension(container: Container, settings: Settings):
    if find_spec("redis") is None:
        raise ModuleNotFoundError("Missing 'redis'. Install 'zayt' with 'redis' extra.")

    for name in settings.redis:
        container.register(make_service(name))
