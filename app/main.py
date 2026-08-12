# pyrefly: ignore [missing-import]
from app.queue.idempotency import is_new_delivery
# pyrefly: ignore [missing-import]
from fastapi import FastAPI, HTTPException, Request
from contextlib import asynccontextmanager
from app.config import settings
from app.github.webhook import verify_github_signature
from app.jobs.schemas import ReviewJob
from app.queue.redis import create_redis_pool

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = await create_redis_pool()

    yield

    await app.state.redis.close()


app = FastAPI(lifespan=lifespan)

REVIEW_ACTIONS = {
    "opened",
    "reopened",
    "synchronize",
}

@app.get("/health")
async def health():
    return {"status": "ok"}
    

@app.post("/github/webhook")
async def github_webhook(request: Request):
    payload = await request.body()

    signature = request.headers.get("X-Hub-Signature-256")

    if not signature:
        raise HTTPException(
            status_code=401,
            detail="Missing GitHub signature",
        )

    if not verify_github_signature(
        payload,
        signature,
        settings.github_webhook_secret,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid GitHub signature",
        )
    
    event = request.headers.get("X-GitHub-Event")
    if event != "pull_request":
        return {
            "status": "ignored",
            "reason": "unsupported event",
        }
    data = await request.json()
    action = data.get("action")
    if action not in REVIEW_ACTIONS:
        return {
            "status": "ignored",
            "reason": f"unsupported action: {action}",
        }
    delivery_id = request.headers.get("X-GitHub-Delivery")
    if not delivery_id:
        raise HTTPException(
            status_code=400,
            detail="Missing delivery ID",
        )
    
    if not await is_new_delivery(
        request.app.state.redis,
        delivery_id,
    ):
        return {
        "status": "ignored",
        "reason": "duplicate delivery",
    }

    pull_request = data["pull_request"]
    repository = data["repository"]

    job = ReviewJob(
        repository=repository["full_name"],
        pr_number=pull_request["number"],
        head_sha=pull_request["head"]["sha"],
        base_sha=pull_request["base"]["sha"],
        event=action,
        delivery_id=delivery_id,
    )

    arq_job = await request.app.state.redis.enqueue_job(
        "process_review",
        job.model_dump(),
    )

    return {
        "status": "accepted",
        "job": job.model_dump(),
    }