from typing import List, Dict, Any, Optional
import uuid

from omnidoc.core.document import Document, Section
from omnidoc.rag.intent import classify_intent
from omnidoc.rag.confidence import score_chunk
from omnidoc.rag.hybrid_metadata import hybrid_metadata
from omnidoc.rag.adaptive import tokens_for_intent


# -------------------------------------------------
# Heuristics
# -------------------------------------------------

def _is_heading(text: str) -> bool:
    """
    Robust heading detection for PDFs / slides.
    """
    if not text:
        return False

    text = text.strip()

    if len(text) < 4 or len(text) > 120:
        return False

    # ALL CAPS
    if text.isupper():
        return True

    # Title Case
    if text.istitle():
        return True

    # Colon-style headings
    if text.endswith(":") and text[0].isupper():
        return True

    return False


def _estimate_tokens(text: str) -> int:
    """
    Cheap, deterministic token estimator.
    """
    return max(1, len(text) // 4)


# -------------------------------------------------
# Main API
# -------------------------------------------------

def semantic_chunk_document(
    doc: Document,
) -> List[Dict[str, Any]]:
    """
    Production-grade semantic chunking for RAG.

    Features:
    - Heading-aware
    - Intent-aware adaptive sizing
    - Token-safe chunking
    - Hybrid metadata (BM25 + vector hints)
    - Deterministic confidence scoring
    """

    chunks: List[Dict[str, Any]] = []

    # 🔥 CRITICAL SAFEGUARD
    if not doc.sections and doc.raw_text:
        doc.sections = [
            Section(page=1, text=doc.raw_text)
        ]

    current_heading: Optional[str] = None
    buffer: List[str] = []
    token_count: int = 0
    current_intent: Optional[str] = None
    max_tokens: int = 300

    def flush():
        nonlocal buffer, token_count, current_intent, max_tokens

        if not buffer:
            return

        text = "\n".join(buffer).strip()
        if not text:
            buffer.clear()
            token_count = 0
            return

        intent = current_intent or classify_intent(text)
        confidence = score_chunk(text)

        chunk = {
            "id": str(uuid.uuid4()),
            "text": text,
            "heading": current_heading,
            "intent": intent,
            "confidence": confidence,
            "metadata": hybrid_metadata(text),
        }

        chunks.append(chunk)

        buffer.clear()
        token_count = 0
        current_intent = None
        max_tokens = 300

    # -------------------------------------------------
    # Iterate document sections
    # -------------------------------------------------

    for sec in doc.sections:
        for raw_line in sec.text.splitlines():
            line = raw_line.strip()
            if not line:
                continue

            # ---------------------------
            # Heading detection
            # ---------------------------
            if _is_heading(line):
                flush()
                current_heading = line
                continue

            # ---------------------------
            # Intent detection (lazy)
            # ---------------------------
            if current_intent is None:
                current_intent = classify_intent(line)
                max_tokens = tokens_for_intent(current_intent)

            # ---------------------------
            # Token-aware buffering
            # ---------------------------
            est_tokens = _estimate_tokens(line)

            if token_count + est_tokens > max_tokens:
                flush()

                # Re-evaluate intent after flush
                current_intent = classify_intent(line)
                max_tokens = tokens_for_intent(current_intent)

            buffer.append(line)
            token_count += est_tokens

    flush()

    return chunks
