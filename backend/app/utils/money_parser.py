import re
from typing import Optional


def parse_indian_money(text: str) -> Optional[int]:
    """
    Parses various Indian currency formats (crore, lakh, L, k, commas) into integer INR.
    Returns None if no money figure is detected.
    """
    if not text:
        return None

    # Normalization
    text = text.replace(",", "")

    # Pattern for Crore: e.g. "1.2 cr", "1.2 crore", "₹ 2.5 crores", "2cr"
    cr_match = re.search(r"(?:rs\.?|inr|₹)?\s*([0-9]+(?:\.[0-9]+)?)\s*(?:cr|crore|crores)\b", text, re.IGNORECASE)
    if cr_match:
        val = float(cr_match.group(1))
        return int(round(val * 10000000))

    # Pattern for Lakh: e.g. "25 lakh", "Rs. 25 lakhs", "₹25L", "6.5 lakhs", "25 lac", "25 lacs"
    lakh_match = re.search(r"(?:rs\.?|inr|₹)?\s*([0-9]+(?:\.[0-9]+)?)\s*(?:lakh|lakhs|lac|lacs|l)\b", text, re.IGNORECASE)
    if lakh_match:
        val = float(lakh_match.group(1))
        return int(round(val * 100000))

    # Pattern for standard numeric Indian formats: e.g. "₹400000", "Rs. 650000", "₹1000000", "Rs 118000"
    num_match = re.search(r"(?:rs\.?|inr|₹)\s*([0-9]{4,12})\b", text, re.IGNORECASE)
    if num_match:
        return int(num_match.group(1))

    # Plain thousands: e.g. "50k", "₹50k"
    k_match = re.search(r"(?:rs\.?|inr|₹)?\s*([0-9]+(?:\.[0-9]+)?)\s*(?:k|thousand)\b", text, re.IGNORECASE)
    if k_match:
        val = float(k_match.group(1))
        return int(round(val * 1000))

    return None
