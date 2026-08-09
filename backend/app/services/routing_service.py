from typing import Dict, Any, Optional, Tuple
from app.utils.text_cleaner import strip_quoted_reply
from app.utils.date_parser import parse_explicit_deadline
from app.services.gemini_service import extract_email_semantics


def determine_routing(
    from_name: Optional[str],
    from_email: str,
    subject: str,
    body: str,
    received_at: str,
    is_reply: bool = False
) -> Dict[str, Any]:
    """
    Applies deterministic Python business routing rules on top of Gemini semantic extraction.
    """
    clean_body = strip_quoted_reply(body)
    semantics = extract_email_semantics(from_name, from_email, subject, body, received_at, is_reply)

    # 1. Skip Rules (Rule 4)
    if semantics.get("is_out_of_office"):
        return {
            "should_skip": True,
            "skip_reason": "out_of_office",
            "assignee_id": None,
            "category": None,
            "priority": None,
            "deal_value_inr": None,
            "company_name": semantics.get("company_name"),
            "due_date": None,
            "confidence": semantics.get("confidence", 0.95),
            "reason": "Out-of-office auto-reply ignored per Rule 4.",
            "is_spurious_candidate": True,
            "title": subject,
            "description": clean_body
        }

    if semantics.get("is_newsletter"):
        return {
            "should_skip": True,
            "skip_reason": "newsletter",
            "assignee_id": None,
            "category": None,
            "priority": None,
            "deal_value_inr": None,
            "company_name": semantics.get("company_name"),
            "due_date": None,
            "confidence": semantics.get("confidence", 0.95),
            "reason": "Newsletter skipped per Rule 4.",
            "is_spurious_candidate": True,
            "title": subject,
            "description": clean_body
        }

    if semantics.get("is_unsolicited_vendor_spam"):
        return {
            "should_skip": True,
            "skip_reason": "vendor_spam",
            "assignee_id": None,
            "category": None,
            "priority": None,
            "deal_value_inr": None,
            "company_name": semantics.get("company_name"),
            "due_date": None,
            "confidence": semantics.get("confidence", 0.95),
            "reason": "Unsolicited vendor pitch selling to us skipped as spam.",
            "is_spurious_candidate": True,
            "title": subject,
            "description": clean_body
        }

    # Extract deadline and check <=72h rule
    due_date, is_within_72h = parse_explicit_deadline(clean_body, received_at)
    if not due_date and semantics.get("due_date"):
        due_date = semantics["due_date"]
        # re-evaluate 72h if possible
        _, is_within_72h = parse_explicit_deadline(due_date, received_at)

    deal_value = semantics.get("deal_value_inr")
    company_name = semantics.get("company_name")
    confidence = semantics.get("confidence", 0.9)

    # 2. Check for Ambiguous / Conflicting Requests
    if semantics.get("is_ambiguous_or_conflicting"):
        priority = "high" if is_within_72h else "medium"
        return {
            "should_skip": False,
            "skip_reason": None,
            "assignee_id": "u_triage",
            "category": "triage",
            "priority": priority,
            "deal_value_inr": None,
            "company_name": company_name,
            "due_date": due_date,
            "confidence": min(confidence, 0.45),
            "reason": "Two distinct asks or conflicting cross-department requests with unconfirmed budget.",
            "is_spurious_candidate": False,
            "title": subject,
            "description": f"Ambiguous inquiry: {clean_body[:200]}"
        }

    # 3. Rule 3: PSU and Government Tenders Override (ALWAYS Aarti, regardless of value)
    if semantics.get("is_psu_or_govt_tender"):
        priority = "high" if is_within_72h else "medium"
        return {
            "should_skip": False,
            "skip_reason": None,
            "assignee_id": "u_aarti",
            "category": "enterprise_rfp",
            "priority": priority,
            "deal_value_inr": deal_value,
            "company_name": company_name,
            "due_date": due_date,
            "confidence": confidence,
            "reason": "Government/PSU tender routed to Aarti Menon per Rule 3 regardless of deal value.",
            "is_spurious_candidate": False,
            "title": subject,
            "description": clean_body
        }

    # 4. Finance Rule: Invoices, POs, GST, payment reminders -> Divya
    if semantics.get("is_finance_invoice_or_billing"):
        is_overdue = "overdue" in clean_body.lower() or is_within_72h
        priority = "high" if is_overdue else "medium"
        return {
            "should_skip": False,
            "skip_reason": None,
            "assignee_id": "u_divya",
            "category": "finance",
            "priority": priority,
            "deal_value_inr": None,  # Invoice amounts are NOT deal values!
            "company_name": company_name,
            "due_date": due_date,
            "confidence": confidence,
            "reason": "Invoice/billing inquiry routed to Divya Rao. Invoice amount excluded from deal value.",
            "is_spurious_candidate": False,
            "title": subject,
            "description": clean_body
        }

    # 5. Marketing Rule: Webinars, sponsorships, PR, content collab -> Meera
    if semantics.get("is_marketing_sponsorship_or_webinar"):
        priority = "high" if is_within_72h else "medium"
        return {
            "should_skip": False,
            "skip_reason": None,
            "assignee_id": "u_meera",
            "category": "marketing",
            "priority": priority,
            "deal_value_inr": deal_value,
            "company_name": company_name,
            "due_date": due_date,
            "confidence": confidence,
            "reason": "Marketing/sponsorship collaboration routed to Meera Iyer.",
            "is_spurious_candidate": False,
            "title": subject,
            "description": clean_body
        }

    # 6. Alliances Rule: Resellers, channel partners, technology integration -> Karan
    if semantics.get("is_alliances_partner"):
        priority = "high" if is_within_72h else "medium"
        return {
            "should_skip": False,
            "skip_reason": None,
            "assignee_id": "u_karan",
            "category": "alliances",
            "priority": priority,
            "deal_value_inr": None,
            "company_name": company_name,
            "due_date": due_date,
            "confidence": confidence,
            "reason": "Reseller/integration partnership proposal routed to Karan Doshi.",
            "is_spurious_candidate": False,
            "title": subject,
            "description": clean_body
        }

    # 7. Enterprise RFP / High Value Deal (> ₹10,00,000) -> Aarti
    if (deal_value and deal_value > 1000000) or semantics.get("is_rfp_or_rfi"):
        priority = "high" if is_within_72h else "medium"
        return {
            "should_skip": False,
            "skip_reason": None,
            "assignee_id": "u_aarti",
            "category": "enterprise_rfp",
            "priority": priority,
            "deal_value_inr": deal_value,
            "company_name": company_name,
            "due_date": due_date,
            "confidence": confidence,
            "reason": "Enterprise RFP/deal above 10 lakh routed to Aarti Menon.",
            "is_spurious_candidate": False,
            "title": subject,
            "description": clean_body
        }

    # 8. SMB Enquiry / Demo Request / Value <= ₹10,00,000 -> Rohit
    if semantics.get("is_smb_product_or_demo") or (deal_value is not None and deal_value <= 1000000):
        # Check priority: "nothing urgent" or no deadline -> low
        if "nothing urgent" in clean_body.lower():
            priority = "low"
        elif is_within_72h:
            priority = "high"
        else:
            priority = "medium" if due_date else "low"

        return {
            "should_skip": False,
            "skip_reason": None,
            "assignee_id": "u_rohit",
            "category": "smb_enquiry",
            "priority": priority,
            "deal_value_inr": deal_value,
            "company_name": company_name,
            "due_date": due_date,
            "confidence": confidence,
            "reason": "SMB inquiry/demo request routed to Rohit Sharma.",
            "is_spurious_candidate": False,
            "title": subject,
            "description": clean_body
        }

    # Default fallback: Triage
    priority = "high" if is_within_72h else "medium"
    return {
        "should_skip": False,
        "skip_reason": None,
        "assignee_id": "u_triage",
        "category": "triage",
        "priority": priority,
        "deal_value_inr": deal_value,
        "company_name": company_name,
        "due_date": due_date,
        "confidence": 0.45,
        "reason": "Unclassified request routed to Triage Queue for manual ops review.",
        "is_spurious_candidate": False,
        "title": subject,
        "description": clean_body
    }
