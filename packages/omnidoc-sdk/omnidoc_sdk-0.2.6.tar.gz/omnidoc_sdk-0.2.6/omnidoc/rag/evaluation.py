# omnidoc/rag/evaluation.py

from typing import Dict, Any, List


def evaluate_rag_response(
    *,
    query: str,
    answer: str,
    retrieved_chunks: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Enterprise RAG evaluation harness.
    """

    if not retrieved_chunks:
        return {
            "score": 0.0,
            "reason": "No retrieved context",
        }

    coverage_score = _coverage(answer, retrieved_chunks)
    confidence_score = sum(c["confidence"] for c in retrieved_chunks) / len(retrieved_chunks)
    source_diversity = len(set(
        src for c in retrieved_chunks for src in c.get("metadata", {}).get("sources", [])
    ))

    final_score = round(
        0.4 * coverage_score +
        0.4 * confidence_score +
        0.2 * min(source_diversity / 3, 1.0),
        2
    )

    return {
        "score": final_score,
        "coverage": round(coverage_score, 2),
        "confidence": round(confidence_score, 2),
        "source_diversity": source_diversity,
        "chunks_used": len(retrieved_chunks),
        "verdict": _verdict(final_score),
    }


def _coverage(answer: str, chunks: List[Dict[str, Any]]) -> float:
    hits = sum(1 for c in chunks if c["text"][:200].lower() in answer.lower())
    return min(hits / len(chunks), 1.0)


def _verdict(score: float) -> str:
    if score >= 0.85:
        return "excellent"
    if score >= 0.7:
        return "good"
    if score >= 0.5:
        return "weak"
    return "unsafe"
