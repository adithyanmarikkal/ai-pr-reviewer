# pyrefly: ignore [missing-import]
from arq import func
# pyrefly: ignore [missing-import]
from arq.connections import RedisSettings

from app.config import settings
from app.jobs.schemas import ReviewJob

async def process_review(ctx, job_data):

    job = ReviewJob.model_validate(job_data)

    print("Received review job")
    print(f"Repository: {job.repository}")
    print(f"PR: #{job.pr_number}")
    print(f"Head SHA: {job.head_sha}")
    print(f"Base SHA: {job.base_sha}")
    print(f"Event: {job.event}")

async def startup(ctx):
    print("Worker started")


async def shutdown(ctx):
    print("Worker shutting down")


class WorkerSettings:
    functions = [process_review]

    redis_settings = RedisSettings.from_dsn(
        settings.redis_url
    )

    on_startup = startup
    on_shutdown = shutdown