# omnidoc/rag/stream.py

from typing import Iterator, Dict, Any
from omnidoc.rag.semantic_chunker import semantic_chunk_document

def stream_chunks(doc) -> Iterator[Dict[str, Any]]:
    """
    Streams semantic chunks incrementally.
    Useful for:
    - Large PDFs
    - Live indexing
    - Agent pipelines
    """

    for chunk in semantic_chunk_document(doc):
        yield chunk
