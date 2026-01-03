from aiomcache import Client, FlagClient

from zayt.conf.settings import Settings
from zayt.di.decorator import service


def make_service(name: str):
    @service(name=name if name != "default" else None)
    async def memcached_service(settings: Settings) -> Client:
        memcached_settings = dict(settings.memcached[name])
        args = []
        kwargs = memcached_settings

        if host := kwargs.pop("host", None):
            args.append(host)
            if port := kwargs.pop("port", None):
                args.append(int(port))

        client = FlagClient(*args, **kwargs)

        yield client
        await client.close()

    return memcached_service
