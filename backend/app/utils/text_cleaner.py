import re


def strip_quoted_reply(body: str) -> str:
    """
    Strips quoted reply chains and forwarded email headers to isolate the newly written message content.
    """
    if not body:
        return ""

    lines = body.splitlines()
    clean_lines = []

    # Common reply delimiters
    reply_patterns = [
        re.compile(r"^-+\s*Original Message\s*-+", re.IGNORECASE),
        re.compile(r"^-+\s*Forwarded message\s*-+", re.IGNORECASE),
        re.compile(r"^On\s+.+wrote:\s*$", re.IGNORECASE),
        re.compile(r"^From:\s*.+@.+", re.IGNORECASE),
        re.compile(r"^_{5,}", re.IGNORECASE),
    ]

    for line in lines:
        stripped = line.strip()
        if stripped.startswith(">"):
            continue

        is_delimiter = False
        for pat in reply_patterns:
            if pat.match(stripped):
                is_delimiter = True
                break

        if is_delimiter:
            break

        clean_lines.append(line)

    cleaned = "\n".join(clean_lines).strip()
    return cleaned if cleaned else body
