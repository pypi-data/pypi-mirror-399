import re
from omnidoc.core.document import Section

HEADING_PATTERN = re.compile(
    r"^[A-Z][A-Za-z0-9 ,:&\-]{5,}$"
)

JUNK_LINE_PATTERN = re.compile(r"^[|=&<>©•]+$")
SLIDE_ARTIFACT_PATTERN = re.compile(r"^[a-z]{1,3}[=}]?$")


def normalize_slide_sections(sections: list[Section]) -> list[Section]:
    """
    Convert slide-style fragments into report-style sections.

    ✔ NO decorative separators
    ✔ Headings preserved
    ✔ Bullets grouped
    ✔ Paragraphs merged
    ✔ Junk removed
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
        buffer = []

    for sec in sections:
        current_page = sec.page

        for raw_line in sec.text.splitlines():
            line = raw_line.strip()
            if not line:
                continue

            # Remove pure junk
            if JUNK_LINE_PATTERN.match(line):
                continue
            if SLIDE_ARTIFACT_PATTERN.match(line):
                continue

            # Heading detected → flush previous content
            if HEADING_PATTERN.match(line):
                flush()
                buffer.append(line)
                continue

            buffer.append(line)

    flush()
    return normalized
