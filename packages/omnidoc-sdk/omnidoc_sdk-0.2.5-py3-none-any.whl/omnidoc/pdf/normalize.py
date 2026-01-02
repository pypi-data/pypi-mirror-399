from omnidoc.core.document import Document, Section, Table
from omnidoc.utils.text import clean_text


def build_document(path: str, sections, tables) -> Document:
    """
    Normalize extracted content into a Document object.

    This is the single defensive boundary:
    - Accepts dicts or domain objects
    - Cleans text
    - Guarantees stable Document output
    """

    normalized_sections: list[Section] = []
    normalized_tables: list[Table] = []

    # -------------------------------------------------
    # Normalize sections (dict → Section, clean text)
    # -------------------------------------------------
    for s in sections:
        if isinstance(s, Section):
            text = clean_text(s.text)
            normalized_sections.append(
                Section(page=s.page, text=text)
            )

        elif isinstance(s, dict):
            text = clean_text(s.get("text", ""))
            normalized_sections.append(
                Section(
                    page=s.get("page", 0),
                    text=text
                )
            )

        else:
            raise TypeError(
                f"Unsupported section type in build_document: {type(s)}"
            )

    # -------------------------------------------------
    # Normalize tables (dict → Table)
    # -------------------------------------------------
    for t in tables:
        if isinstance(t, Table):
            normalized_tables.append(t)

        elif isinstance(t, dict):
            normalized_tables.append(
                Table(
                    page=t.get("page", 0),
                    headers=t.get("headers", []),
                    rows=t.get("rows", [])
                )
            )

        else:
            raise TypeError(
                f"Unsupported table type in build_document: {type(t)}"
            )

    # -------------------------------------------------
    # Build raw text (final canonical text)
    # -------------------------------------------------
    raw_text = "\n".join(
        sec.text for sec in normalized_sections if sec.text
    )

    return Document(
        metadata={
            "file": path,
            "pages": len(normalized_sections),
            "type": "pdf"
        },
        sections=normalized_sections,
        tables=normalized_tables,
        raw_text=raw_text
    )
