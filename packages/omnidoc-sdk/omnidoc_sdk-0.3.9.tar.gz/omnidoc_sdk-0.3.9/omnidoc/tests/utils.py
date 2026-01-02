from omnidoc.loader.router import load_document

def run_basic_checks(path: str):
    doc = load_document(path)

    assert doc is not None
    assert doc.raw_text is not None
    assert len(doc.raw_text) > 20

    # RAG guarantees
    assert hasattr(doc, "chunks")
    assert len(doc.chunks) > 0

    for c in doc.chunks:
        assert "text" in c
        assert "intent" in c
        assert "confidence" in c

    return doc
