from pydantic import BaseModel, field_validator
from typing import Optional, List, Any


class EmailItem(BaseModel):
    email_id: str
    thread_id: str
    message_index: Optional[int] = 0
    from_name: Optional[str] = None
    from_email: str
    to: Optional[str] = None
    cc: Optional[List[str]] = None
    subject: str
    body: str
    received_at: str
    attachments: Optional[List[str]] = None
    is_reply: Optional[bool] = False


class IngestRequest(BaseModel):
    candidate_id: str
    emails: List[EmailItem]

    @field_validator("candidate_id")
    @classmethod
    def normalize_candidate(cls, v: str) -> str:
        return v.strip().lower()


class IngestResponse(BaseModel):
    processed: int
    tasks_created: int
    tasks_updated: int
    skipped: int
    errors: List[Any] = []
