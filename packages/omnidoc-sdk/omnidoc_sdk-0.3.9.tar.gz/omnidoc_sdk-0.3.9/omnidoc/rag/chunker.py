import hashlib
from typing import List
from omnidoc.core.document import Document, Section, Table
from omnidoc.rag.schema import SemanticChunk


def _hash(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]


def semantic_chunk_document(
    doc: Document,
    *,
    max_chars: int = 1200,
    overlap: int = 150
) -> List[SemanticChunk]:
    """
    Production-grade semantic chunking for RAG.
    """

    chunks: List[SemanticChunk] = []

    # ---------------------------
    # 1️⃣ Section-based chunking
    # ---------------------------
    for sec in doc.sections:
        buffer = ""
        start_page = sec.page

        for para in sec.text.split("\n\n"):
            para = para.strip()
            if not para:
                continue

            if len(buffer) + len(para) <= max_chars:
                buffer += "\n\n" + para if buffer else para
            else:
                chunks.append(
                    SemanticChunk(
                        id=_hash(buffer),
                        text=buffer,
                        section=_infer_section_title(buffer),
                        page_start=start_page,
                        page_end=sec.page,
                        intent=_infer_intent(buffer),
                        metadata={"source": "section"}
                    )
                )
                buffer = para[-(max_chars - overlap):]

        if buffer:
            chunks.append(
                SemanticChunk(
                    id=_hash(buffer),
                    text=buffer,
                    section=_infer_section_title(buffer),
                    page_start=start_page,
                    page_end=sec.page,
                    intent=_infer_intent(buffer),
                    metadata={"source": "section"}
                )
            )

    # ---------------------------
    # 2️⃣ Table / metric chunks
    # ---------------------------
    for table in doc.tables:
        flat = " | ".join(
            " ".join(row) for row in table.rows if row
        )

        if flat.strip():
            chunks.append(
                SemanticChunk(
                    id=_hash(flat),
                    text=flat,
                    section="TABLE",
                    page_start=table.page,
                    page_end=table.page,
                    intent="metric",
                    metadata={"source": "table"}
                )
            )

    return chunks


# ---------------------------
# Helpers
# ---------------------------

def _infer_section_title(text: str) -> str | None:
    lines = text.splitlines()
    if lines and lines[0].isupper():
        return lines[0][:80]
    return None


def _infer_intent(text: str) -> str:
    if any(c.isdigit() for c in text):
        return "metric"
    if text.isupper():
        return "heading"
    return "narrative"
