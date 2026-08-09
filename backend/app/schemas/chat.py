from pydantic import BaseModel, field_validator
from typing import Optional, Dict, Any


class ChatRequest(BaseModel):
    candidate_id: str
    query: str

    @field_validator("candidate_id")
    @classmethod
    def normalize_candidate(cls, v: str) -> str:
        return v.strip().lower()


class ChatResponse(BaseModel):
    answer: str
    supporting_data: Dict[str, Any] = {}
