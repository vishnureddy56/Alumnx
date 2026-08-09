from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Any
from app.schemas.enums import ALLOWED_ASSIGNEES, ALLOWED_CATEGORIES, ALLOWED_PRIORITIES


class InvalidEnumValueException(Exception):
    def __init__(self, field: str, received: Any, allowed: List[str]):
        self.field = field
        self.received = received
        self.allowed = allowed
        super().__init__(f"Invalid value '{received}' for field '{field}'. Allowed: {allowed}")


class TaskCreate(BaseModel):
    candidate_id: str
    source_email_id: str
    thread_id: str
    title: str
    description: Optional[str] = None
    assignee_id: str
    category: str
    priority: str
    due_date: Optional[str] = None
    deal_value_inr: Optional[int] = None
    company_name: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)

    @field_validator("candidate_id")
    @classmethod
    def normalize_candidate(cls, v: str) -> str:
        return v.strip().lower()

    @field_validator("assignee_id")
    @classmethod
    def validate_assignee(cls, v: str) -> str:
        if v not in ALLOWED_ASSIGNEES:
            raise InvalidEnumValueException(field="assignee_id", received=v, allowed=ALLOWED_ASSIGNEES)
        return v

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        if v not in ALLOWED_CATEGORIES:
            raise InvalidEnumValueException(field="category", received=v, allowed=ALLOWED_CATEGORIES)
        return v

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: str) -> str:
        if v not in ALLOWED_PRIORITIES:
            raise InvalidEnumValueException(field="priority", received=v, allowed=ALLOWED_PRIORITIES)
        return v


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assignee_id: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[str] = None
    deal_value_inr: Optional[int] = None
    company_name: Optional[str] = None
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)

    @field_validator("assignee_id")
    @classmethod
    def validate_assignee(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ALLOWED_ASSIGNEES:
            raise InvalidEnumValueException(field="assignee_id", received=v, allowed=ALLOWED_ASSIGNEES)
        return v

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ALLOWED_CATEGORIES:
            raise InvalidEnumValueException(field="category", received=v, allowed=ALLOWED_CATEGORIES)
        return v

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ALLOWED_PRIORITIES:
            raise InvalidEnumValueException(field="priority", received=v, allowed=ALLOWED_PRIORITIES)
        return v


class TaskCreateResponse(BaseModel):
    task_id: str
    candidate_id: str
    source_email_id: str
    created_at: str


class TaskResponse(BaseModel):
    task_id: str
    candidate_id: str
    source_email_id: str
    thread_id: str
    title: str
    description: Optional[str] = None
    assignee_id: str
    category: str
    priority: str
    due_date: Optional[str] = None
    deal_value_inr: Optional[int] = None
    company_name: Optional[str] = None
    confidence: float
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
