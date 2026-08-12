# pyrefly: ignore [missing-import]
from arq.connections import ArqRedis


async def is_new_delivery(
    redis: ArqRedis,
    delivery_id: str,
) -> bool:

    key = f"webhook:{delivery_id}"

    created = await redis.set(
        key,
        "processed",
        nx=True,
        ex=3600,
    )

    return created is True