from redis.asyncio import Redis

from zayt.conf.settings import Settings
from zayt.di.decorator import service


def make_service(name: str):
    @service(name=name if name != "default" else None)
    async def redis_service(settings: Settings) -> Redis:
        redis_settings = dict(settings.redis[name])

        if url := redis_settings.pop("url", None):
            redis = Redis.from_url(url, **redis_settings)
        else:
            redis = Redis(**redis_settings)

        await redis.initialize()
        yield redis
        await redis.aclose()

    return redis_service
