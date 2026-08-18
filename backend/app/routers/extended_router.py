import json
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.task import Task
from app.models.processed_email import ProcessedEmail
from app.models.thread_history import ThreadHistory
from app.schemas.email import IngestRequest, IngestResponse
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.stats import StatsResponse
from app.services.ingestion_service import process_email_batch
from app.services.chat_service import answer_chat_query

router = APIRouter(tags=["RouteIQ API"])


@router.post("/ingest", response_model=IngestResponse)
def ingest_emails(payload: IngestRequest, db: Session = Depends(get_db)):
    """
    POST /ingest: Synchronously processes a batch of emails, classifies them,
    applies business routing rules, updates tasks or creates new tasks, and records audit logs.
    """
    return process_email_batch(payload.candidate_id, payload.emails, db)


@router.get("/api/tasks")
def list_api_tasks(
    candidate_id: Optional[str] = Query("vishnureddynandyala1234@gmail.com"),
    db: Session = Depends(get_db)
):
    """
    GET /api/tasks: Returns all tasks enriched with processing metadata, including skipped emails.
    """
    norm_candidate = candidate_id.strip().lower() if candidate_id else "vishnureddynandyala1234@gmail.com"

    tasks = db.query(Task).filter(Task.candidate_id == norm_candidate).order_by(Task.created_at.desc()).all()
    processed_emails = db.query(ProcessedEmail).filter(
        ProcessedEmail.candidate_id == norm_candidate
    ).order_by(ProcessedEmail.created_at.desc()).all()

    return {
        "tasks": [
            {
                "task_id": t.task_id,
                "candidate_id": t.candidate_id,
                "source_email_id": t.source_email_id,
                "thread_id": t.thread_id,
                "title": t.title,
                "description": t.description,
                "assignee_id": t.assignee_id,
                "category": t.category,
                "priority": t.priority,
                "due_date": t.due_date,
                "deal_value_inr": t.deal_value_inr,
                "company_name": t.company_name,
                "confidence": t.confidence,
                "created_at": t.created_at,
                "updated_at": t.updated_at
            }
            for t in tasks
        ],
        "processed_emails": [
            {
                "email_id": pe.email_id,
                "thread_id": pe.thread_id,
                "from_name": pe.from_name,
                "from_email": pe.from_email,
                "subject": pe.subject,
                "received_at": pe.received_at,
                "decision": pe.decision,
                "skip_reason": pe.skip_reason,
                "category": pe.category,
                "assignee_id": pe.assignee_id,
                "priority": pe.priority,
                "confidence": pe.confidence,
                "routing_reason": pe.routing_reason,
                "task_id": pe.task_id
            }
            for pe in processed_emails
        ]
    }


@router.get("/api/stats", response_model=StatsResponse)
def get_stats(
    candidate_id: Optional[str] = Query("vishnureddynandyala1234@gmail.com"),
    db: Session = Depends(get_db)
):
    """
    GET /api/stats: Aggregate counts: processed, created, updated, skipped, spurious rate, etc.
    """
    norm_candidate = candidate_id.strip().lower() if candidate_id else "vishnureddynandyala1234@gmail.com"

    processed = db.query(ProcessedEmail).filter(ProcessedEmail.candidate_id == norm_candidate).count()
    created = db.query(ProcessedEmail).filter(
        ProcessedEmail.candidate_id == norm_candidate,
        ProcessedEmail.decision == "created"
    ).count()
    updated = db.query(ProcessedEmail).filter(
        ProcessedEmail.candidate_id == norm_candidate,
        ProcessedEmail.decision == "updated"
    ).count()
    skipped = db.query(ProcessedEmail).filter(
        ProcessedEmail.candidate_id == norm_candidate,
        ProcessedEmail.decision == "skipped"
    ).count()
    spurious = db.query(ProcessedEmail).filter(
        ProcessedEmail.candidate_id == norm_candidate,
        ProcessedEmail.is_spurious_candidate == True
    ).count()

    spurious_rate = round(spurious / max(processed, 1), 4) if processed > 0 else 0.0

    tasks = db.query(Task).filter(Task.candidate_id == norm_candidate).all()

    categories: Dict[str, int] = {}
    assignees: Dict[str, int] = {}
    priorities: Dict[str, int] = {}
    total_deal_value = 0
    rfps_with_no_value = 0

    for t in tasks:
        categories[t.category] = categories.get(t.category, 0) + 1
        assignees[t.assignee_id] = assignees.get(t.assignee_id, 0) + 1
        priorities[t.priority] = priorities.get(t.priority, 0) + 1

        if t.category == "enterprise_rfp":
            if t.deal_value_inr is not None:
                total_deal_value += t.deal_value_inr
            else:
                rfps_with_no_value += 1

    multi_threads = db.query(
        ThreadHistory.thread_id
    ).filter(
        ThreadHistory.candidate_id == norm_candidate,
        ThreadHistory.update_type == "update"
    ).distinct().all()

    return StatsResponse(
        processed=processed,
        tasks_created=created,
        tasks_updated=updated,
        skipped=skipped,
        spurious_count=spurious,
        spurious_rate=spurious_rate,
        categories=categories,
        assignees=assignees,
        priorities=priorities,
        total_deal_value_inr=total_deal_value,
        rfps_with_no_stated_value=rfps_with_no_value,
        threads_updated_multiple_times=[t[0] for t in multi_threads]
    )


@router.post("/api/chat", response_model=ChatResponse)
def chat_query(payload: ChatRequest, db: Session = Depends(get_db)):
    """
    POST /api/chat: Grounded conversational assistant querying stored DB state.
    """
    res = answer_chat_query(payload.candidate_id, payload.query, db)
    return ChatResponse(
        answer=res["answer"],
        supporting_data=res["supporting_data"]
    )


@router.get("/health")
def health_check():
    return {"status": "healthy", "service": "RouteIQ", "version": "1.0.0"}
