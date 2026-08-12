import asyncio

# pyrefly: ignore [missing-import]
from arq import create_pool
# pyrefly: ignore [missing-import]
from arq.connections import RedisSettings

from app.config import settings


async def main():

    redis = await create_pool(
        RedisSettings.from_dsn(settings.redis_url)
    )

    job = await redis.enqueue_job(
        "process_review",
        {
            "repository": "adithyan/test-repo",
            "pr_number": 42,
            "head_sha": "abc123",
        },
    )

    print("Job ID:", job.job_id)

    await redis.close()


if __name__ == "__main__":
    asyncio.run(main())