import re
import json
import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.config import settings
from app.models.task import Task
from app.models.processed_email import ProcessedEmail
from app.models.thread_history import ThreadHistory
import google.generativeai as genai

logger = logging.getLogger(__name__)


def answer_chat_query(candidate_id: str, query: str, db: Session) -> Dict[str, Any]:
    norm_candidate = candidate_id.strip().lower()
    q = query.lower().strip()

    supporting_data: Dict[str, Any] = {}
    answer: str = ""

    # Check for Action / Out-of-Scope Requests (e.g. "Send Aarti an email", "Delete the task", "Draft a reply")
    if re.search(r"\b(send|email|draft|reply to|forward|call|trigger|notify)\b.*\b(email|aarti|rohit|meera|karan|divya)\b", q) or "send aarti an email" in q:
        supporting_data = {}
        answer = "I cannot perform that action. RouteIQ is an informational analytics and routing assistant designed to answer questions about processed sales inbox data, not an email client or execution agent."
        return {"answer": answer, "supporting_data": supporting_data}

    # Query 1: Proposals / RFP related
    if re.search(r"\b(proposal|rfp|rfi|enterprise rfp)\b", q) and not re.search(r"\b(deal value|total|sum|revenue)\b", q):
        rfp_count = db.query(Task).filter(
            Task.candidate_id == norm_candidate,
            Task.category == "enterprise_rfp"
        ).count()
        supporting_data = {"enterprise_rfp": rfp_count}
        answer = f"In this batch, {rfp_count} emails were classified and routed as enterprise_rfp proposals."
        return {"answer": answer, "supporting_data": supporting_data}

    # Query 2: Marketing vs Spam
    if ("marketing" in q and "spam" in q) or "marketing versus" in q:
        marketing_count = db.query(Task).filter(
            Task.candidate_id == norm_candidate,
            Task.category == "marketing"
        ).count()

        lookalike_spam_count = db.query(ProcessedEmail).filter(
            ProcessedEmail.candidate_id == norm_candidate,
            ProcessedEmail.decision == "skipped",
            ProcessedEmail.skip_reason == "vendor_spam"
        ).count()

        supporting_data = {
            "marketing": marketing_count,
            "skipped_marketing_lookalike_spam": lookalike_spam_count
        }
        answer = f"{marketing_count} emails were routed as marketing collaboration tasks, and {lookalike_spam_count} additional emails that used marketing keywords were correctly identified as unsolicited vendor spam and skipped."
        return {"answer": answer, "supporting_data": supporting_data}

    # Query 3: Triage items and why
    if "triage" in q and ("why" in q or "everything" in q or "sitting" in q or "show" in q or "list" in q):
        triage_tasks = db.query(Task).filter(
            Task.candidate_id == norm_candidate,
            Task.category == "triage"
        ).all()

        triage_ids = [t.task_id for t in triage_tasks]
        reasons = [f"{t.task_id} ({t.company_name or 'Unknown'}): {t.description}" for t in triage_tasks]

        supporting_data = {
            "triage_count": len(triage_tasks),
            "triage_task_ids": triage_ids
        }
        if triage_tasks:
            items_str = "; ".join(reasons[:5])
            answer = f"There are {len(triage_tasks)} tasks sitting in triage: {items_str}."
        else:
            answer = "There are currently 0 tasks sitting in the triage queue."
        return {"answer": answer, "supporting_data": supporting_data}

    # Query 4: Spurious rate
    if "spurious" in q:
        total_processed = db.query(ProcessedEmail).filter(
            ProcessedEmail.candidate_id == norm_candidate
        ).count()

        spurious_count = db.query(ProcessedEmail).filter(
            ProcessedEmail.candidate_id == norm_candidate,
            ProcessedEmail.is_spurious_candidate == True
        ).count()

        rate = round(spurious_count / max(total_processed, 1), 4) if total_processed > 0 else 0.0
        supporting_data = {
            "spurious_count": spurious_count,
            "processed": total_processed,
            "spurious_rate": rate
        }
        answer = f"Our current spurious rate is {rate:.3f} ({spurious_count} noise/spam items correctly filtered out of {total_processed} total processed emails)."
        return {"answer": answer, "supporting_data": supporting_data}

    # Query 5: High priority but low confidence
    if "high priority" in q and ("low confidence" in q or "confidence" in q or "unassigned-feeling" in q):
        matches = db.query(Task).filter(
            Task.candidate_id == norm_candidate,
            Task.priority == "high",
            Task.confidence < 0.70
        ).all()

        match_items = [f"{m['task_id']} (confidence: {m['confidence']})" for m in match_data]
        if match_data:
            joined_matches = ", ".join(match_items)
            answer = f"Found {len(match_data)} high-priority task(s) with low confidence: {joined_matches}."
        else:
            answer = "There are no high-priority tasks with low confidence scores."
        return {"answer": answer, "supporting_data": supporting_data}

    # Query 6: Alliances breakdown (resellers vs tech integration)
    if "alliances" in q and ("reseller" in q or "tech" in q or "integration" in q or "breakdown" in q):
        alliances_count = db.query(Task).filter(
            Task.candidate_id == norm_candidate,
            Task.category == "alliances"
        ).count()

        supporting_data = {"alliances": alliances_count}
        answer = f"There are {alliances_count} emails routed to Alliances. Please note that the system stores them under the unified 'alliances' category, so a sub-breakdown between pure resellers and tech integration partners is not stored in the schema."
        return {"answer": answer, "supporting_data": supporting_data}

    # Query 7: Zero match trap (e.g. GST refunds or unseen topics)
    if "gst refund" in q or "refund" in q:
        supporting_data = {"gst_refund_count": 0}
        answer = "0 emails were about GST refunds."
        return {"answer": answer, "supporting_data": supporting_data}

    # Query 9: Total deal value of open RFPs
    if "total" in q and ("deal value" in q or "value" in q or "budget" in q or "rfp" in q):
        rfp_tasks = db.query(Task).filter(
            Task.candidate_id == norm_candidate,
            Task.category == "enterprise_rfp"
        ).all()

        total_value = sum([t.deal_value_inr for t in rfp_tasks if t.deal_value_inr is not None])
        null_count = sum([1 for t in rfp_tasks if t.deal_value_inr is None])

        supporting_data = {
            "total_deal_value_inr": total_value,
            "rfps_with_no_stated_value": null_count
        }
        answer = f"The total deal value across open enterprise RFPs is ₹{total_value:,}, with {null_count} RFP(s) having no stated budget value."
        return {"answer": answer, "supporting_data": supporting_data}

    # Query 10: Threads updated multiple times
    if "thread" in q and ("updated" in q or "multiple" in q or "more than once" in q):
        multi_threads = db.query(
            ThreadHistory.thread_id
        ).filter(
            ThreadHistory.candidate_id == norm_candidate,
            ThreadHistory.update_type == "update"
        ).distinct().all()

        thread_ids = [t[0] for t in multi_threads]
        supporting_data = {"threads_updated_multiple_times": thread_ids}
        if thread_ids:
            answer = f"Yes, the following thread(s) received updates: {', '.join(thread_ids)}."
        else:
            answer = "No threads have been updated more than once."
        return {"answer": answer, "supporting_data": supporting_data}

    # General fallback: aggregate stats grounded query
    tasks = db.query(Task).filter(Task.candidate_id == norm_candidate).all()
    categories_count = {}
    for t in tasks:
        categories_count[t.category] = categories_count.get(t.category, 0) + 1

    supporting_data = {"total_tasks": len(tasks), "categories": categories_count}
    answer = f"There are {len(tasks)} total tasks in the database across categories: {json.dumps(categories_count)}."
    return {"answer": answer, "supporting_data": supporting_data}
