# pyrefly: ignore [missing-import]
from arq import create_pool
# pyrefly: ignore [missing-import]
from arq.connections import ArqRedis, RedisSettings

from app.config import settings


async def create_redis_pool() -> ArqRedis:
    return await create_pool(
        RedisSettings.from_dsn(settings.redis_url)
    )