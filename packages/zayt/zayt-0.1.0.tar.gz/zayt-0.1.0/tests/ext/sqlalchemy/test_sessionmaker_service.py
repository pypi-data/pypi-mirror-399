import pytest
from sqlalchemy import String, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from zayt.conf.defaults import default_settings
from zayt.conf.settings import Settings
from zayt.ext.sqlalchemy.service import sessionmaker_service


class BaseA(DeclarativeBase):
    pass


class ModelA(BaseA):
    __tablename__ = "model"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))


class BaseB(DeclarativeBase):
    pass


class ModelB(BaseB):
    __tablename__ = "model"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))


async def test_session_options():
    settings = Settings(
        default_settings
        | {
            "sqlalchemy": {
                "connections": {
                    "default": {
                        "url": "sqlite+aiosqlite:///:memory:",
                    },
                },
                "session": {
                    "options": {
                        "info": {"framework": "zayt"},
                    },
                },
            },
        }
    )

    engine = create_async_engine(settings.sqlalchemy.connections.default.url)

    sessionmaker = await sessionmaker_service(settings, {"default": engine})
    async with sessionmaker() as session:
        assert session.info == {"framework": "zayt"}


async def test_session_class():
    class MySession(AsyncSession):
        pass

    settings = Settings(
        default_settings
        | {
            "sqlalchemy": {
                "connections": {
                    "default": {
                        "url": "sqlite+aiosqlite:///:memory:",
                    },
                },
                "session": {
                    "options": {
                        "class": MySession,
                    },
                },
            },
        }
    )

    engine = create_async_engine(settings.sqlalchemy.connections.default.url)

    sessionmaker = await sessionmaker_service(settings, {"default": engine})
    async with sessionmaker() as session:
        assert session.__class__ == MySession


@pytest.mark.parametrize(
    "base_a, base_b",
    [
        (
            f"{BaseA.__module__}:{BaseA.__qualname__}",
            f"{BaseB.__module__}:{BaseB.__qualname__}",
        ),
        (BaseA, BaseB),
    ],
    ids=["str", "class"],
)
async def test_binds(base_a, base_b):
    settings = Settings(
        default_settings
        | {
            "sqlalchemy": {
                "connections": {
                    "conn_a": {
                        "url": "sqlite+aiosqlite:///:memory:",
                    },
                    "conn_b": {
                        "url": "sqlite+aiosqlite:///:memory:",
                    },
                },
                "session": {
                    "binds": {
                        base_a: "conn_a",
                        base_b: "conn_b",
                    },
                },
            },
        }
    )

    engine_a = create_async_engine(settings.sqlalchemy.connections.conn_a.url)
    engine_b = create_async_engine(settings.sqlalchemy.connections.conn_b.url)

    sessionmaker = await sessionmaker_service(
        settings, {"conn_a": engine_a, "conn_b": engine_b}
    )
    async with sessionmaker() as session:
        assert session.binds[BaseA] == engine_a
        assert session.binds[BaseB] == engine_b


async def test_sessiomaker_without_default_connection(log_output):
    settings = Settings(
        default_settings
        | {
            "sqlalchemy": {
                "connections": {
                    "conn": {
                        "url": "sqlite+aiosqlite:///:memory:",
                    },
                },
            },
        }
    )

    engine = create_async_engine(settings.sqlalchemy.connections.conn.url)

    sessionmaker = await sessionmaker_service(settings, {"conn": engine})
    async with sessionmaker() as session:
        assert session.bind is engine

    assert (
        log_output.entries[0]["event"]
        == "No default engine found, using next available"
    )
    assert log_output.entries[0]["engine"] == "conn"


@pytest.mark.parametrize(
    "base_a, base_b",
    [
        (
            f"{BaseA.__module__}:{BaseA.__qualname__}",
            f"{BaseB.__module__}:{BaseB.__qualname__}",
        ),
        (BaseA, BaseB),
    ],
    ids=["str", "class"],
)
async def test_binds_model(base_a, base_b):
    settings = Settings(
        default_settings
        | {
            "sqlalchemy": {
                "connections": {
                    "conn_a": {
                        "url": "sqlite+aiosqlite:///:memory:",
                    },
                    "conn_b": {
                        "url": "sqlite+aiosqlite:///:memory:",
                    },
                },
                "session": {
                    "binds": {
                        base_a: "conn_a",
                        base_b: "conn_b",
                    },
                },
            },
        }
    )

    engine_a = create_async_engine(settings.sqlalchemy.connections.conn_a.url)
    async with engine_a.connect() as conn:
        await conn.run_sync(BaseA.metadata.create_all)

    engine_b = create_async_engine(settings.sqlalchemy.connections.conn_b.url)
    async with engine_b.connect() as conn:
        await conn.run_sync(BaseB.metadata.create_all)

    sessionmaker = await sessionmaker_service(
        settings, {"conn_a": engine_a, "conn_b": engine_b}
    )
    async with sessionmaker() as session:
        session.add_all(
            [
                ModelA(id=1, name="A"),
                ModelB(id=1, name="B"),
            ]
        )
        await session.commit()

    async with sessionmaker() as session:
        name_a = await session.scalar(select(ModelA.name).where(ModelA.id == 1))
        name_b = await session.scalar(select(ModelB.name).where(ModelB.id == 1))

        assert name_a == "A"
        assert name_b == "B"


async def test_binds_with_invalid_connection_should_fail():
    settings = Settings(
        default_settings
        | {
            "sqlalchemy": {
                "connections": {
                    "default": {
                        "url": "sqlite+aiosqlite:///:memory:",
                    },
                },
                "session": {
                    "binds": {
                        f"{BaseA.__module__}:{BaseA.__qualname__}": "invalid",
                    },
                },
            },
        }
    )

    with pytest.raises(ValueError, match="No engine with name 'invalid'"):
        await sessionmaker_service(settings, {"default": None})
