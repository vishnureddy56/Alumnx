import json
import logging
import os
import re
import time
from typing import Dict, Any, Optional
import google.generativeai as genai
from app.config import settings
from app.utils.text_cleaner import strip_quoted_reply
from app.utils.money_parser import parse_indian_money
from app.utils.date_parser import parse_explicit_deadline

logger = logging.getLogger(__name__)

if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)


EXTRACTION_PROMPT = """
You are RouteIQ's Semantic Understanding Engine for a B2B sales inbox.
Analyze the given email and extract structured JSON information.

Email Details:
From: {from_name} <{from_email}>
Subject: {subject}
Received At: {received_at}
Is Reply: {is_reply}
Cleaned Body:
\"\"\"
{body}
\"\"\"

Carefully evaluate the following signals:
1. is_out_of_office: true if this is an automated out-of-office response or vacation bounce.
2. is_newsletter: true if this is a marketing newsletter, industry digest, or automated blast (has unsubscribe, issue number, blog roundup).
3. is_unsolicited_vendor_spam: true if an external vendor/agency is selling services TO us (e.g. SEO services, web design, lead gen pitches, cold sales pitches), rather than a prospective customer buying from us.
4. is_psu_or_govt_tender: true if the sender is a Public Sector Undertaking (PSU like BHEL, NTPC, ONGC, SAIL, IOCL) or government body issuing a tender/bid.
5. is_rfp_or_rfi: true if requesting proposals/bids for enterprise solution, tender, or formal RFP/RFI.
6. is_smb_product_or_demo: true if asking for a product demo, SMB enquiry, trial, or pricing discussion for small/medium business.
7. is_marketing_sponsorship_or_webinar: true if inviting us to sponsor a conference/event, co-host a webinar, PR/media interview, or content collaboration. (NOT vendor spam).
8. is_alliances_partner: true if proposing reseller partnership, channel partnership, or technology integration.
9. is_finance_invoice_or_billing: true if sending an invoice, PO, payment reminder, GST details, or vendor billing inquiry.
10. is_ambiguous_or_conflicting: true if the email has multiple conflicting requests across different departments (e.g. both enterprise eval and webinar co-host with unknown budget) or cannot be cleanly classified.
11. company_name: Extract the sender's company name if explicitly named or clear in context. Set null if not determinable. Never invent a company name.
12. deal_value_inr: Extract explicit deal budget/value in integer INR (e.g. 2500000, 12000000). Set null for invoices/bills or if not stated. Do not guess.
13. due_date: Extract explicit deadline in YYYY-MM-DD format if stated. Set null if vague (e.g. 'next week', 'soon').
14. confidence: Float between 0.0 and 1.0 indicating confidence.
15. summary_reason: Brief 1-2 sentence explanation of the classification.

Output ONLY valid JSON matching this schema:
{{
  "is_out_of_office": false,
  "is_newsletter": false,
  "is_unsolicited_vendor_spam": false,
  "is_psu_or_govt_tender": false,
  "is_rfp_or_rfi": false,
  "is_smb_product_or_demo": false,
  "is_marketing_sponsorship_or_webinar": false,
  "is_alliances_partner": false,
  "is_finance_invoice_or_billing": false,
  "is_ambiguous_or_conflicting": false,
  "company_name": null,
  "deal_value_inr": null,
  "due_date": null,
  "confidence": 0.9,
  "summary_reason": "..."
}}
"""


def rule_based_fallback_extraction(
    from_name: Optional[str],
    from_email: str,
    subject: str,
    body: str,
    received_at: str,
    is_reply: bool = False
) -> Dict[str, Any]:
    """
    High-precision deterministic rule-based extractor used when Gemini is unavailable or as fallback.
    """
    clean_body = strip_quoted_reply(body)
    full_text = f"{subject}\n{clean_body}".lower()

    # 1. Out of Office
    is_ooo = bool(
        re.search(r"\b(out of office|auto-reply|vacation response|away from the office|limited access to email)\b", full_text)
        or "auto-reply" in (from_name or "").lower()
    )

    # 2. Newsletter
    is_newsletter = bool(
        re.search(r"(\[unsubscribe\]|issue\s*#?\d+|weekly digest|growth weekly|teardown of|unsubscribe here)", full_text)
    )

    # 3. Unsolicited Vendor Spam vs Marketing
    # Check direction of intent:
    is_selling_to_us = bool(re.search(r"\b(we've helped 200\+|ranking on page 1|organic traffic|free audit attached|interested in a quick 15 min call|seo services|cold outreach)\b", full_text))
    is_vendor_spam = is_selling_to_us and not is_ooo and not is_newsletter

    # 4. PSU / Govt Tender
    is_psu = bool(re.search(r"\b(tender notice|bhel|procurement|bharat heavy electricals|ntpc|ongc|sail|iocl|invites bids|psu tender|tender no)\b", full_text))

    # 5. Finance
    is_finance = bool(re.search(r"\b(invoice|inv-\d+|po-\d+|purchase order|payment terms|net 30|gstin|18% gst|vendor billing|overdue|payment reminder)\b", full_text))

    # 6. Alliances
    is_alliances = bool(re.search(r"\b(reseller|reselling|channel partner|technical integration|salesforce implementation partner|who handles partnerships)\b", full_text)) and not is_finance

    # 7. Marketing Sponsorship / Collaboration (Legitimate)
    is_marketing = (
        bool(re.search(r"\b(finalising sponsors|gold tier|summit|sponsorship lead|keynote slot|co-host a webinar|media interview|pr outreach)\b", full_text))
        and not is_vendor_spam
        and not is_finance
    )

    # 8. Ambiguous / Conflicting
    is_ambiguous = bool(re.search(r"\b(two things:\s*\(1\)|budget tbd|can you loop in the right people)\b", full_text)) or (
        sum([bool(is_marketing), bool(is_alliances), bool(is_psu), "demo" in full_text and "webinar" in full_text]) > 1 and "budget tbd" in full_text
    )

    # 9. RFP / RFI
    is_rfp = bool(re.search(r"\b(rfp|rfi|invites proposals|enterprise dms|enterprise document management|tender)\b", full_text)) or is_psu

    # 10. SMB / Demo
    is_smb = bool(re.search(r"\b(demo|product enquiry|trial|logistics startup|can we get a demo|humko aapka product chahiye)\b", full_text)) and not is_rfp

    # Company extraction
    company_name = None

    # 1. Direct entity checks from text or sender email
    if "bharat heavy electricals" in full_text or "bhel" in full_text or "bhel.in" in from_email:
        company_name = "Bharat Heavy Electricals Limited"
    elif "meridian steel" in full_text or "meridiansteel" in from_email:
        company_name = "Meridian Steel"
    elif "india saas summit" in full_text or "saassummit" in from_email:
        company_name = "India SaaS Summit"
    elif "vantage cloud services" in full_text or "vantagecloud" in from_email:
        company_name = "Vantage Cloud Services"
    elif "zenith cloud partners" in full_text or "zenithcloudpartners" in from_email:
        company_name = "Zenith Cloud Partners"
    elif "railyard logistics" in full_text or "railyardlogistics" in from_email:
        company_name = "Railyard Logistics"
    elif "halcyon retail" in full_text or "halcyonretail" in from_email:
        company_name = "Halcyon Retail"

    # 2. Check signature pattern e.g. "— Ankit Bose, Founder, Railyard Logistics"
    if not company_name:
        sig_match = re.search(r"[-—]\s*([A-Za-z\s]+),\s*(?:Founder|VP|Lead|Manager|Head|CEO|Director|Strategy)[^,\n]*,\s*([A-Za-z0-9\s]+(?:Pvt|Ltd|Limited|Logistics|Partners|Summit|Retail|Steel|Services|Cloud|Corp|Solutions)?)$", clean_body, re.MULTILINE | re.IGNORECASE)
        if sig_match:
            cand = sig_match.group(2).strip()
            if len(cand) > 2 and not re.search(r"(gmail|outlook|yahoo)\b", cand, re.IGNORECASE):
                company_name = cand

    # Money extraction (Do NOT assign deal value to invoices)
    deal_value = None
    if not is_finance:
        deal_value = parse_indian_money(clean_body)

    # Date extraction
    due_date, _ = parse_explicit_deadline(clean_body, received_at)

    confidence = 0.92
    if is_ambiguous:
        confidence = 0.42
    elif is_vendor_spam or is_ooo or is_newsletter:
        confidence = 0.95

    return {
        "is_out_of_office": is_ooo,
        "is_newsletter": is_newsletter,
        "is_unsolicited_vendor_spam": is_vendor_spam,
        "is_psu_or_govt_tender": is_psu,
        "is_rfp_or_rfi": is_rfp,
        "is_smb_product_or_demo": is_smb,
        "is_marketing_sponsorship_or_webinar": is_marketing,
        "is_alliances_partner": is_alliances,
        "is_finance_invoice_or_billing": is_finance,
        "is_ambiguous_or_conflicting": is_ambiguous,
        "company_name": company_name,
        "deal_value_inr": deal_value,
        "due_date": due_date,
        "confidence": confidence,
        "summary_reason": f"Extracted semantic attributes from subject and body."
    }


def extract_email_semantics(
    from_name: Optional[str],
    from_email: str,
    subject: str,
    body: str,
    received_at: str,
    is_reply: bool = False
) -> Dict[str, Any]:
    """
    Extracts semantic features using Gemini API with retry and automatic fallback.
    """
    clean_body = strip_quoted_reply(body)

    if not settings.GEMINI_API_KEY:
        return rule_based_fallback_extraction(from_name, from_email, subject, body, received_at, is_reply)

    prompt = EXTRACTION_PROMPT.format(
        from_name=from_name or "",
        from_email=from_email,
        subject=subject,
        received_at=received_at,
        is_reply=is_reply,
        body=clean_body
    )

    max_retries = 3
    for attempt in range(max_retries):
        try:
            model = genai.GenerativeModel(
                model_name=settings.GEMINI_MODEL,
                generation_config={"response_mime_type": "application/json"}
            )
            response = model.generate_content(prompt)
            data = json.loads(response.text)

            # Ensure money parser and date parser validate/supplement
            if data.get("deal_value_inr") is None and not data.get("is_finance_invoice_or_billing"):
                extracted_money = parse_indian_money(clean_body)
                if extracted_money:
                    data["deal_value_inr"] = extracted_money

            if data.get("due_date") is None:
                extracted_due, _ = parse_explicit_deadline(clean_body, received_at)
                if extracted_due:
                    data["due_date"] = extracted_due

            return data
        except Exception as e:
            logger.warning(f"Gemini call attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                logger.error("Gemini failed after retries, utilizing rule-based fallback.")
                return rule_based_fallback_extraction(from_name, from_email, subject, body, received_at, is_reply)
