import structlog
from sqlalchemy.engine.url import URL, make_url
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from zayt.util.import_item import import_item
from zayt.conf.settings import Settings
from zayt.di.container import Container
from zayt.di.decorator import service

logger = structlog.get_logger(__name__)


def _get_url(settings: Settings) -> URL:
    if url := settings.get("url"):
        url = make_url(url)
        if username := settings.get("username"):
            url = url.set(username=username)
        if password := settings.get("password"):
            url = url.set(password=password)
        if query := settings.get("query"):
            url = url.set(query=query)
    else:
        kwargs = {}

        if drivername := settings.get("drivername"):
            kwargs["drivername"] = drivername
        if host := settings.get("host"):
            kwargs["host"] = host
        if port := settings.get("port"):
            kwargs["port"] = int(port)
        if database := settings.get("database"):
            kwargs["database"] = database
        if username := settings.get("username"):
            kwargs["username"] = username
        if password := settings.get("password"):
            kwargs["password"] = password
        if query := settings.get("query"):
            kwargs["query"] = query

        url = URL.create(**kwargs)

    return url


def make_engine_service(name: str):
    @service(name=name if name != "default" else None)
    async def engine_service(settings: Settings) -> AsyncEngine:
        sa_settings = settings.sqlalchemy.connections[name]

        url = _get_url(sa_settings)
        options = dict(sa_settings.get("options", {}))

        engine = create_async_engine(url, **options)
        yield engine
        await engine.dispose()

    return engine_service


@service
async def engine_dict_service(
    settings: Settings, di: Container
) -> dict[str, AsyncEngine]:
    return {
        db: await di.get(AsyncEngine, name=db if db != "default" else None)
        for db in settings.sqlalchemy.connections
    }


@service
async def sessionmaker_service(
    settings: Settings, engines_map: dict[str, AsyncEngine]
) -> async_sessionmaker:
    session_settings = settings.sqlalchemy.get("session", {})

    args = []
    kwargs = dict(session_settings.get("options", {}))

    if binds := session_settings.get("binds"):
        binds_config = {}
        for mapper, engine_name in binds.items():
            if isinstance(mapper, str):
                mapper = import_item(mapper)
            if engine := engines_map.get(engine_name):
                binds_config[mapper] = engine
            else:
                raise ValueError(f"No engine with name '{engine_name}'")

        kwargs["binds"] = binds_config
    else:
        engine = engines_map.get("default")
        if not engine:
            name, engine = next(iter(engines_map.items()))
            logger.warning(
                "No default engine found, using next available",
                engine=name,
            )
        args.append(engine)

    if class_ := kwargs.pop("class", None):
        kwargs["class_"] = class_

    return async_sessionmaker(*args, **kwargs)


@service(scoped=True)
async def async_session(sessionmaker: async_sessionmaker) -> AsyncSession:
    async with sessionmaker() as session:
        yield session
