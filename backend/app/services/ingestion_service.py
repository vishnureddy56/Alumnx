import json
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.task import Task
from app.models.processed_email import ProcessedEmail
from app.models.thread_history import ThreadHistory
from app.schemas.email import EmailItem, IngestResponse
from app.services.routing_service import determine_routing
from app.utils.text_cleaner import strip_quoted_reply


def generate_task_id() -> str:
    return f"tsk_{uuid.uuid4().hex[:6]}"


def current_iso_time() -> str:
    return datetime.now(timezone.utc).isoformat()


def process_email_batch(candidate_id: str, emails: List[EmailItem], db: Session) -> IngestResponse:
    norm_candidate = candidate_id.strip().lower()

    processed_count = 0
    created_count = 0
    updated_count = 0
    skipped_count = 0
    errors: List[Dict[str, Any]] = []

    for email_item in emails:
        try:
            processed_count += 1
            now_str = current_iso_time()

            # 1. Check if email already processed under this candidate_id (Idempotency - Run 2)
            existing_proc = db.query(ProcessedEmail).filter(
                ProcessedEmail.candidate_id == norm_candidate,
                ProcessedEmail.email_id == email_item.email_id
            ).first()

            if existing_proc:
                # Already processed. No-op to preserve exact idempotency.
                continue

            # 2. Check for existing task under this thread (Thread reconciliation - Run 3)
            existing_task = db.query(Task).filter(
                Task.candidate_id == norm_candidate,
                Task.thread_id == email_item.thread_id
            ).first()

            # Determine routing / semantic extraction
            routing_res = determine_routing(
                from_name=email_item.from_name,
                from_email=email_item.from_email,
                subject=email_item.subject,
                body=email_item.body,
                received_at=email_item.received_at,
                is_reply=bool(email_item.is_reply or existing_task)
            )

            # If existing task found on thread -> Update task instead of creating duplicate
            if existing_task:
                changed_fields = {}
                if routing_res["deal_value_inr"] is not None and routing_res["deal_value_inr"] != existing_task.deal_value_inr:
                    existing_task.deal_value_inr = routing_res["deal_value_inr"]
                    changed_fields["deal_value_inr"] = routing_res["deal_value_inr"]

                if routing_res["due_date"] is not None and routing_res["due_date"] != existing_task.due_date:
                    existing_task.due_date = routing_res["due_date"]
                    changed_fields["due_date"] = routing_res["due_date"]

                if routing_res["priority"] is not None and routing_res["priority"] != existing_task.priority:
                    existing_task.priority = routing_res["priority"]
                    changed_fields["priority"] = routing_res["priority"]

                existing_task.updated_at = now_str

                # Record thread history
                prev_history_count = db.query(ThreadHistory).filter(
                    ThreadHistory.candidate_id == norm_candidate,
                    ThreadHistory.thread_id == email_item.thread_id
                ).count()

                th = ThreadHistory(
                    candidate_id=norm_candidate,
                    thread_id=email_item.thread_id,
                    task_id=existing_task.task_id,
                    email_id=email_item.email_id,
                    update_type="update",
                    update_count=prev_history_count + 1,
                    changed_fields=json.dumps(changed_fields),
                    summary=f"Thread updated with {email_item.subject}",
                    created_at=now_str
                )
                db.add(th)

                # Record processed email
                pe = ProcessedEmail(
                    email_id=email_item.email_id,
                    candidate_id=norm_candidate,
                    thread_id=email_item.thread_id,
                    message_index=email_item.message_index or 0,
                    from_name=email_item.from_name,
                    from_email=email_item.from_email,
                    to_email=email_item.to,
                    subject=email_item.subject,
                    body=email_item.body,
                    received_at=email_item.received_at,
                    is_reply=email_item.is_reply or True,
                    attachments=json.dumps(email_item.attachments or []),
                    decision="updated",
                    skip_reason=None,
                    category=existing_task.category,
                    assignee_id=existing_task.assignee_id,
                    priority=existing_task.priority,
                    deal_value_inr=existing_task.deal_value_inr,
                    company_name=existing_task.company_name,
                    due_date=existing_task.due_date,
                    confidence=routing_res["confidence"],
                    routing_reason=f"Thread update on existing task {existing_task.task_id}: {routing_res['reason']}",
                    task_id=existing_task.task_id,
                    is_spurious_candidate=False,
                    created_at=now_str
                )
                db.add(pe)
                db.commit()

                updated_count += 1
                continue

            # Check if this email should be skipped
            if routing_res["should_skip"]:
                pe = ProcessedEmail(
                    email_id=email_item.email_id,
                    candidate_id=norm_candidate,
                    thread_id=email_item.thread_id,
                    message_index=email_item.message_index or 0,
                    from_name=email_item.from_name,
                    from_email=email_item.from_email,
                    to_email=email_item.to,
                    subject=email_item.subject,
                    body=email_item.body,
                    received_at=email_item.received_at,
                    is_reply=bool(email_item.is_reply),
                    attachments=json.dumps(email_item.attachments or []),
                    decision="skipped",
                    skip_reason=routing_res["skip_reason"],
                    category=None,
                    assignee_id=None,
                    priority=None,
                    deal_value_inr=None,
                    company_name=routing_res["company_name"],
                    due_date=None,
                    confidence=routing_res["confidence"],
                    routing_reason=routing_res["reason"],
                    task_id=None,
                    is_spurious_candidate=routing_res["is_spurious_candidate"],
                    created_at=now_str
                )
                db.add(pe)
                db.commit()

                skipped_count += 1
                continue

            # Otherwise, create brand new task
            new_task_id = generate_task_id()
            task = Task(
                task_id=new_task_id,
                candidate_id=norm_candidate,
                source_email_id=email_item.email_id,
                thread_id=email_item.thread_id,
                title=f"{email_item.subject} — {routing_res['company_name'] or email_item.from_name or 'Inbound'}",
                description=routing_res["description"],
                assignee_id=routing_res["assignee_id"],
                category=routing_res["category"],
                priority=routing_res["priority"],
                due_date=routing_res["due_date"],
                deal_value_inr=routing_res["deal_value_inr"],
                company_name=routing_res["company_name"],
                confidence=routing_res["confidence"],
                created_at=now_str,
                updated_at=now_str
            )
            db.add(task)

            # Record thread history
            th = ThreadHistory(
                candidate_id=norm_candidate,
                thread_id=email_item.thread_id,
                task_id=new_task_id,
                email_id=email_item.email_id,
                update_type="create",
                update_count=1,
                changed_fields=json.dumps({"initial": True}),
                summary=f"Initial task created from {email_item.subject}",
                created_at=now_str
            )
            db.add(th)

            # Record processed email
            pe = ProcessedEmail(
                email_id=email_item.email_id,
                candidate_id=norm_candidate,
                thread_id=email_item.thread_id,
                message_index=email_item.message_index or 0,
                from_name=email_item.from_name,
                from_email=email_item.from_email,
                to_email=email_item.to,
                subject=email_item.subject,
                body=email_item.body,
                received_at=email_item.received_at,
                is_reply=bool(email_item.is_reply),
                attachments=json.dumps(email_item.attachments or []),
                decision="created",
                skip_reason=None,
                category=routing_res["category"],
                assignee_id=routing_res["assignee_id"],
                priority=routing_res["priority"],
                deal_value_inr=routing_res["deal_value_inr"],
                company_name=routing_res["company_name"],
                due_date=routing_res["due_date"],
                confidence=routing_res["confidence"],
                routing_reason=routing_res["reason"],
                task_id=new_task_id,
                is_spurious_candidate=False,
                created_at=now_str
            )
            db.add(pe)
            db.commit()

            created_count += 1

        except Exception as e:
            db.rollback()
            errors.append({"email_id": getattr(email_item, "email_id", "unknown"), "error": str(e)})

    return IngestResponse(
        processed=processed_count,
        tasks_created=created_count,
        tasks_updated=updated_count,
        skipped=skipped_count,
        errors=errors
    )
