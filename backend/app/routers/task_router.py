import uuid
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.task import Task
from app.schemas.enums import TEAM_ROSTER
from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskCreateResponse,
    TaskResponse
)

router = APIRouter(tags=["Task API"])


def generate_task_id() -> str:
    return f"tsk_{uuid.uuid4().hex[:6]}"


def current_iso_time() -> str:
    return datetime.now(timezone.utc).isoformat()


@router.post("/tasks", response_model=TaskCreateResponse, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    task_id = generate_task_id()
    now_str = current_iso_time()

    # Check for existing task under candidate_id and source_email_id to maintain integrity
    existing = db.query(Task).filter(
        Task.candidate_id == payload.candidate_id,
        Task.source_email_id == payload.source_email_id
    ).first()

    if existing:
        return TaskCreateResponse(
            task_id=existing.task_id,
            candidate_id=existing.candidate_id,
            source_email_id=existing.source_email_id,
            created_at=existing.created_at
        )

    task = Task(
        task_id=task_id,
        candidate_id=payload.candidate_id,
        source_email_id=payload.source_email_id,
        thread_id=payload.thread_id,
        title=payload.title,
        description=payload.description,
        assignee_id=payload.assignee_id,
        category=payload.category,
        priority=payload.priority,
        due_date=payload.due_date,
        deal_value_inr=payload.deal_value_inr,
        company_name=payload.company_name,
        confidence=payload.confidence,
        created_at=now_str,
        updated_at=now_str
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return TaskCreateResponse(
        task_id=task.task_id,
        candidate_id=task.candidate_id,
        source_email_id=task.source_email_id,
        created_at=task.created_at
    )


@router.patch("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: str, payload: TaskUpdate, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    task.updated_at = current_iso_time()
    db.commit()
    db.refresh(task)

    return task


@router.get("/tasks", response_model=List[TaskResponse])
def list_tasks(
    candidate_id: str = Query(..., description="Mandatory lowercased candidate email"),
    thread_id: Optional[str] = Query(None),
    source_email_id: Optional[str] = Query(None),
    assignee_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    norm_candidate = candidate_id.strip().lower()
    query = db.query(Task).filter(Task.candidate_id == norm_candidate)

    if thread_id:
        query = query.filter(Task.thread_id == thread_id)
    if source_email_id:
        query = query.filter(Task.source_email_id == source_email_id)
    if assignee_id:
        query = query.filter(Task.assignee_id == assignee_id)

    return query.order_by(Task.created_at.desc()).all()


@router.delete("/tasks/{task_id}")
def delete_task(task_id: str, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
    return {"status": "deleted", "task_id": task_id}


@router.get("/users")
def get_users():
    return {"team": TEAM_ROSTER}
