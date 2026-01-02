# omnidoc/rag/streaming_chunker.py

from typing import Iterator, Dict, Any
from omnidoc.core.document import Document, Section
from omnidoc.rag.intent import classify_intent
from omnidoc.rag.confidence import score_chunk
from omnidoc.rag.hybrid_metadata import hybrid_metadata

DEFAULT_MAX_TOKENS = 350


def stream_semantic_chunks(
    doc: Document,
    *,
    max_tokens: int = DEFAULT_MAX_TOKENS,
) -> Iterator[Dict[str, Any]]:
    """
    Streaming semantic chunk generator for RAG ingestion.
    Yields chunks incrementally (memory-safe).
    """

    current_heading = None
    buffer: list[str] = []
    token_count = 0

    def flush():
        nonlocal buffer, token_count
        if not buffer:
            return None

        text = "\n".join(buffer).strip()
        buffer.clear()
        token_count = 0

        intent = classify_intent(text)
        confidence = score_chunk(text)

        return {
            "text": text,
            "heading": current_heading,
            "intent": intent,
            "confidence": confidence,
            "metadata": hybrid_metadata(text),
        }

    for sec in doc.sections:
        lines = sec.text.splitlines()

        # Heading detection
        if len(lines) == 1 and lines[0].istitle():
            chunk = flush()
            if chunk:
                yield chunk
            current_heading = lines[0]
            continue

        for line in lines:
            est_tokens = max(1, len(line) // 4)

            if token_count + est_tokens > max_tokens:
                chunk = flush()
                if chunk:
                    yield chunk

            buffer.append(line)
            token_count += est_tokens

    chunk = flush()
    if chunk:
        yield chunk
