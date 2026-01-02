from typing import Dict, Any
from omnidoc.core.document import Document, Section, Table


def document_to_json(doc: Document) -> Dict[str, Any]:
    """
    Convert Document object into JSON-serializable dict.
    """

    return {
        "metadata": doc.metadata,
        "sections": [
            {
                "page": sec.page,
                "text": sec.text
            }
            for sec in doc.sections
        ],
        "tables": [
            {
                "page": tbl.page,
                "headers": tbl.headers,
                "rows": tbl.rows
            }
            for tbl in doc.tables
        ],
        "raw_text": doc.raw_text
    }


def document_to_toon(doc: Document) -> Dict[str, Any]:
    """
    TOON = Task-Oriented Object Notation
    (agent-friendly, chunked, semantic)
    """

    return {
        "type": "document",
        "source": doc.metadata.get("file"),
        "pages": doc.metadata.get("pages"),
        "content": [
            {
                "kind": "section",
                "page": sec.page,
                "text": sec.text
            }
            for sec in doc.sections
        ],
        "tables": [
            {
                "kind": "table",
                "page": tbl.page,
                "headers": tbl.headers,
                "rows": tbl.rows
            }
            for tbl in doc.tables
        ]
    }
