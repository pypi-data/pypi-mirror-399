import re

def clean_text(text: str) -> str:
    if not text:
        return ""

    text = text.replace("\x0c", " ")

    lines_out = []

    for raw_line in text.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        # -------------------------------------------------
        # 🚨 NEVER DROP NUMERIC LINES
        # -------------------------------------------------
        if any(c.isdigit() for c in line):
            lines_out.append(line)
            continue

        # -------------------------------------------------
        # Drop pure symbol noise
        # -------------------------------------------------
        if not any(c.isalnum() for c in line):
            continue

        # -------------------------------------------------
        # Drop decorative separators
        # -------------------------------------------------
        if re.fullmatch(r"[|=_•©\-–—]+", line):
            continue

        # -------------------------------------------------
        # Drop slide artifacts like "e=", "ly }"
        # -------------------------------------------------
        if re.fullmatch(r"[a-z]{1,2}[=}]$", line):
            continue

        # -------------------------------------------------
        # Drop OCR hallucination tokens
        # -------------------------------------------------
        if (
            len(line.split()) <= 3
            and not re.search(r"[aeiouAEIOU]", line)
        ):
            continue

        # -------------------------------------------------
        # Normalize bullets
        # -------------------------------------------------
        line = re.sub(r"^[•>\-–—]+", "", line).strip()

        lines_out.append(line)

    text = "\n".join(lines_out)

    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)

    return text.strip()
