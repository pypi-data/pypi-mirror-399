# omnidoc/rag/hybrid_metadata.py

import hashlib

def hybrid_metadata(text: str) -> dict:
    """
    Hybrid retrieval metadata:
    - BM25 lexical hints
    - Vector embedding placeholders
    """

    keywords = list(set(word.lower() for word in text.split() if len(word) > 4))[:15]

    return {
        "bm25_keywords": keywords,
        "embedding_hint": hashlib.sha1(text.encode()).hexdigest(),
        "length": len(text),
    }
