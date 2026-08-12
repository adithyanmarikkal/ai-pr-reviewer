# pyrefly: ignore [missing-import]
from fastapi import FastAPI, HTTPException, Request

from app.config import settings
from app.github.webhook import verify_github_signature

app = FastAPI()

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
    return {
        "status": "accepted",
        "action": action,
    }