# pyrefly: ignore [missing-import]
from pydantic import BaseModel


class ReviewJob(BaseModel):
    repository: str
    pr_number: int

    head_sha: str
    base_sha: str

    event: str
    delivery_id: str