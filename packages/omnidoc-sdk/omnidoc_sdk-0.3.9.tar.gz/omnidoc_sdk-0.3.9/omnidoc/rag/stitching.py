# omnidoc/rag/stitcher.py

from typing import List, Dict, Any
from difflib import SequenceMatcher


def stitch_chunks(
    documents: List[Dict[str, Any]],
    *,
    similarity_threshold: float = 0.75,
) -> List[Dict[str, Any]]:
    """
    Cross-document semantic stitching engine.
    """

    stitched: List[Dict[str, Any]] = []

    def similar(a: str, b: str) -> float:
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    for doc in documents:
        for chunk in doc.get("chunks", []):
            merged = False

            for existing in stitched:
                # Heading + intent alignment
                if (
                    chunk["intent"] == existing["intent"]
                    and chunk["heading"]
                    and existing["heading"]
                    and similar(chunk["heading"], existing["heading"]) > similarity_threshold
                ):
                    existing["text"] += "\n\n" + chunk["text"]
                    existing["sources"].append(doc["metadata"]["file"])
                    existing["confidence"] = max(
                        existing["confidence"], chunk["confidence"]
                    )
                    merged = True
                    break

            if not merged:
                stitched.append({
                    "heading": chunk["heading"],
                    "intent": chunk["intent"],
                    "text": chunk["text"],
                    "confidence": chunk["confidence"],
                    "sources": [doc["metadata"]["file"]],
                })

    return stitched
