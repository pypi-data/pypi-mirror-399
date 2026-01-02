import re
from omnidoc.core.document import Section

# Strong heading heuristic (slides / decks)
HEADING_PATTERN = re.compile(
    r"^[A-Z][A-Za-z0-9 ,:&\-]{5,}$"
)

JUNK_LINE_PATTERN = re.compile(r"[|=&<>©•]+")
SLIDE_ARTIFACT_PATTERN = re.compile(r"[a-z]{1,3}[=}]?")

def normalize_slide_sections(sections: list[Section]) -> list[Section]:
    """
    Convert slide-style fragments into report-style sections.

    Guarantees:
    - Headings preserved (no decorative lines)
    - Bullets grouped
    - Paragraphs merged
    - Junk removed
    """

    normalized: list[Section] = []
    buffer: list[str] = []
    current_page: int | None = None

    def flush():
        nonlocal buffer, current_page
        if not buffer:
            return

        text = "\n".join(buffer).strip()
        if text:
            normalized.append(
                Section(
                    page=current_page or 0,
                    text=text
                )
            )
        buffer.clear()

    for sec in sections:
        current_page = sec.page

        for raw_line in sec.text.splitlines():
            line = raw_line.strip()
            if not line:
                continue

            # ---------------------------------
            # Drop junk / slide artifacts
            # ---------------------------------
            if JUNK_LINE_PATTERN.fullmatch(line):
                continue
            if SLIDE_ARTIFACT_PATTERN.fullmatch(line):
                continue
            if re.fullmatch(r"-{3,}", line):
                continue  # 🔥 HARD STOP: no separators ever

            # ---------------------------------
            # Heading detection
            # ---------------------------------
            if HEADING_PATTERN.match(line):
                flush()
                buffer.append(line)  # ✅ heading only
                continue

            # ---------------------------------
            # Normal content
            # ---------------------------------
            buffer.append(line)

        flush()

    return normalized
