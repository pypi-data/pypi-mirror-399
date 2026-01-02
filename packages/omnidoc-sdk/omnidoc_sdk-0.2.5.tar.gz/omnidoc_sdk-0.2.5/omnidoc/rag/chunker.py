def chunk_document(doc, max_chars=1200):
    """
    Heading-aware chunking for RAG.
    """
    chunks = []
    buffer = ""

    for sec in doc.sections:
        if len(buffer) + len(sec.text) > max_chars:
            chunks.append(buffer.strip())
            buffer = ""
        buffer += sec.text + "\n"

    if buffer:
        chunks.append(buffer.strip())

    return chunks
