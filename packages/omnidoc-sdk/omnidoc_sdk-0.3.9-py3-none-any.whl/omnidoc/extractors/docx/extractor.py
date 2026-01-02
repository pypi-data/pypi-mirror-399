from typing import List
from docx import Document as WordDocument

from omnidoc.core.document import Document, Section, Table


class DocxExtractor:
    """
    Production-grade DOCX extractor.

    Guarantees:
    - Heading-aware sections
    - Clean semantic boundaries
    - RAG-ready output
    """

    def extract(self, path: str) -> Document:
        doc = WordDocument(path)

        sections: List[Section] = []
        tables: List[Table] = []

        buffer: List[str] = []
        current_heading: str | None = None
        page = 1

        def flush():
            nonlocal buffer
            if not buffer:
                return

            text = "\n".join(buffer).strip()
            if text:
                sections.append(
                    Section(
                        page=page,
                        text=text
                    )
                )
            buffer = []

        # -------------------------------------------------
        # Paragraph processing
        # -------------------------------------------------
        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue

            style = para.style.name if para.style else ""

            # -------------------------
            # Heading detection
            # -------------------------
            if style.startswith("Heading"):
                flush()

                current_heading = text
                sections.append(
                    Section(
                        page=page,
                        text=current_heading
                    )
                )
                continue

            # -------------------------
            # Normal content
            # -------------------------
            buffer.append(text)

        flush()

        # -------------------------------------------------
        # Table extraction
        # -------------------------------------------------
        for t in doc.tables:
            rows = []
            for row in t.rows:
                rows.append([cell.text.strip() for cell in row.cells])

            tables.append(
                Table(
                    page=page,
                    headers=rows[0] if rows else [],
                    rows=rows[1:] if len(rows) > 1 else []
                )
            )

        raw_text = "\n".join(sec.text for sec in sections)

        return Document(
            metadata={
                "file": path,
                "pages": 1,
                "type": "docx",
            },
            sections=sections,
            tables=tables,
            raw_text=raw_text,
        )
