from importlib.util import find_spec

from zayt.conf.settings import Settings
from zayt.di.container import Container
from zayt.ext.sqlalchemy.service import (
    async_session,
    engine_dict_service,
    make_engine_service,
    sessionmaker_service,
)


def init_extension(container: Container, settings: Settings):
    if find_spec("sqlalchemy") is None:
        raise ModuleNotFoundError(
            "Missing 'sqlalchemy'. Install 'zayt' with 'sqlalchemy' extra."
        )

    for name in settings.sqlalchemy.connections:
        container.register(make_engine_service(name))

    container.register(engine_dict_service)
    container.register(sessionmaker_service)
    container.register(async_session)
