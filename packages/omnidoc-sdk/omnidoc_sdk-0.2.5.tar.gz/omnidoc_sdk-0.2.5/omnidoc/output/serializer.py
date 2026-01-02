from typing import Dict, Any, List
import re

from omnidoc.postprocess.metrics import normalize_metrics
from omnidoc.rag.chunker import chunk_document


# -------------------------------------------------
# JSON OUTPUT (Analytics / RAG / API)
# -------------------------------------------------
def to_json(doc) -> Dict[str, Any]:
    return {
        "metadata": doc.metadata,
        "sections": [
            {
                "page": s.page,
                "text": s.text
            }
            for s in doc.sections
        ],
        "tables": [
            {
                "page": t.page,
                "headers": t.headers,
                "rows": t.rows
            }
            for t in doc.tables
        ],
        "metrics": _unique_metrics(doc),
        "chunks": chunk_document(doc),
    }


# -------------------------------------------------
# TOON OUTPUT (Agent-native)
# -------------------------------------------------
def to_toon(doc) -> Dict[str, Any]:
    return {
        "document": {
            "source": doc.metadata.get("file"),
            "pages": doc.metadata.get("pages"),
            "type": doc.metadata.get("type"),
        },
        "reasoning": {
            "sections": [
                {
                    "intent": _infer_intent(s.text),
                    "content": s.text,
                }
                for s in doc.sections
            ]
        },
        "artifacts": {
            "tables": [
                {
                    "page": t.page,
                    "rows": t.rows,
                }
                for t in doc.tables
            ],
            "metrics": _unique_metrics(doc),
        },
        "confidence": _estimate_confidence(doc),
    }


# -------------------------------------------------
# Helpers
# -------------------------------------------------
def _infer_intent(text: str) -> str:
    """
    Robust heading detection (slide + report safe)
    """
    lines = text.splitlines()
    first = lines[0].strip()

    # Underlined headings
    if len(lines) > 1 and re.fullmatch(r"-{3,}", lines[1].strip()):
        return "heading"

    # Short declarative headings
    if (
        len(first) < 80
        and not first.endswith(".")
        and first[0].isupper()
    ):
        return "heading"

    return "content"


def _unique_metrics(doc) -> List[Dict[str, Any]]:
    """
    Deduplicate normalized metrics across tables
    """
    seen = set()
    metrics = []

    for table in doc.tables:
        for metric in normalize_metrics(table):
            key = (
                metric.get("name"),
                metric.get("value"),
                metric.get("unit"),
            )
            if key not in seen:
                seen.add(key)
                metrics.append(metric)

    return metrics


def _estimate_confidence(doc) -> float:
    score = 1.0

    if not doc.sections:
        score -= 0.4

    if not doc.raw_text or len(doc.raw_text) < 500:
        score -= 0.3

    if not doc.tables:
        score -= 0.1

    return round(max(score, 0.1), 2)
