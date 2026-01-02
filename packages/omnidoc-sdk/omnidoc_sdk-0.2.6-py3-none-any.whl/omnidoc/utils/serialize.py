from typing import Dict, Any
from omnidoc.rag.chunker import semantic_chunk_document


def document_to_json(doc) -> Dict[str, Any]:
    chunks = semantic_chunk_document(doc)

    return {
        "metadata": doc.metadata,
        "sections": [
            {"page": s.page, "text": s.text}
            for s in doc.sections
        ],
        "tables": [
            {"page": t.page, "headers": t.headers, "rows": t.rows}
            for t in doc.tables
        ],
        "chunks": [
            {
                "id": c.id,
                "text": c.text,
                "section": c.section,
                "page_start": c.page_start,
                "page_end": c.page_end,
                "intent": c.intent,
                "metadata": c.metadata,
            }
            for c in chunks
        ]
    }


def document_to_toon(doc) -> Dict[str, Any]:
    chunks = semantic_chunk_document(doc)

    return {
        "document": doc.metadata,
        "reasoning": [
            {
                "chunk_id": c.id,
                "intent": c.intent,
                "content": c.text
            }
            for c in chunks
        ],
        "confidence": round(
            min(1.0, 0.6 + 0.05 * len(chunks)), 2
        )
    }
