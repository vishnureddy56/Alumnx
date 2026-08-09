import re
from datetime import datetime, timedelta
from typing import Optional, Tuple


MONTHS = {
    "jan": 1, "january": 1,
    "feb": 2, "february": 2,
    "mar": 3, "march": 3,
    "apr": 4, "april": 4,
    "may": 5,
    "jun": 6, "june": 6,
    "jul": 7, "july": 7,
    "aug": 8, "august": 8,
    "sep": 9, "september": 9,
    "oct": 10, "october": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12,
}


def parse_received_at(received_at_str: str) -> Optional[datetime]:
    if not received_at_str:
        return None
    try:
        # Handle ISO strings with offset or Z
        clean = received_at_str.replace("Z", "+00:00")
        return datetime.fromisoformat(clean)
    except Exception:
        # Fallback parsing
        for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(received_at_str[:19], fmt)
            except Exception:
                pass
    return None


def parse_explicit_deadline(text: str, received_at_str: Optional[str] = None) -> Tuple[Optional[str], bool]:
    """
    Parses explicit deadline from text. Returns (due_date_iso_YYYY_MM_DD, is_within_72h).
    Returns (None, False) if no explicit deadline is present.
    """
    if not text:
        return None, False

    rec_dt = parse_received_at(received_at_str) if received_at_str else None
    base_year = rec_dt.year if rec_dt else 2026
    base_month = rec_dt.month if rec_dt else 8

    # Check for "tomorrow" / "tomorrow EOD"
    if re.search(r"\btomorrow\b", text, re.IGNORECASE) and rec_dt:
        due_dt = rec_dt + timedelta(days=1)
        due_date_str = due_dt.strftime("%Y-%m-%d")
        return due_date_str, True

    # Check DD-MM-YYYY (e.g. 03-08-2026)
    dmy_match = re.search(r"\b(\d{1,2})[-/](\d{1,2})[-/](\d{4})\b", text)
    if dmy_match:
        day = int(dmy_match.group(1))
        month = int(dmy_match.group(2))
        year = int(dmy_match.group(3))
        try:
            due_dt = datetime(year, month, day)
            due_date_str = due_dt.strftime("%Y-%m-%d")
            is_within_72 = False
            if rec_dt:
                diff_hours = (due_dt.date() - rec_dt.date()).total_seconds() / 3600.0
                is_within_72 = 0 <= diff_hours <= 72
            return due_date_str, is_within_72
        except Exception:
            pass

    # Check e.g. "12th August 2026", "12 Aug 2026", "11th August"
    text_date_match = re.search(
        r"\b(\d{1,2})(?:st|nd|rd|th)?\s+(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)(?:\s+(\d{4}))?\b",
        text,
        re.IGNORECASE
    )
    if text_date_match:
        day = int(text_date_match.group(1))
        month_str = text_date_match.group(2).lower()
        month = MONTHS.get(month_str, base_month)
        year = int(text_date_match.group(3)) if text_date_match.group(3) else base_year

        try:
            due_dt = datetime(year, month, day)
            due_date_str = due_dt.strftime("%Y-%m-%d")
            is_within_72 = False
            if rec_dt:
                diff_hours = (due_dt.date() - rec_dt.date()).total_seconds() / 3600.0
                is_within_72 = 0 <= diff_hours <= 72
            return due_date_str, is_within_72
        except Exception:
            pass

    # Check day only if near context mentions explicit date e.g. "20th ko hai", "by 20th"
    day_match = re.search(r"\b(?:by|before|on|review)\s+(\d{1,2})(?:st|nd|rd|th)\b", text, re.IGNORECASE)
    if day_match and rec_dt:
        day = int(day_match.group(1))
        try:
            due_dt = datetime(base_year, base_month, day)
            due_date_str = due_dt.strftime("%Y-%m-%d")
            diff_hours = (due_dt.date() - rec_dt.date()).total_seconds() / 3600.0
            is_within_72 = 0 <= diff_hours <= 72
            return due_date_str, is_within_72
        except Exception:
            pass

    return None, False
