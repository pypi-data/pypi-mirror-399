def text_blocks_only(blocks):
    """
    Keep only meaningful text blocks.
    Removes decorative / empty / noise blocks.
    """
    filtered = []

    for b in blocks:
        text = (b.text or "").strip()

        # Drop empty
        if not text:
            continue

        # Drop pure symbols
        if len(text) <= 3 and not any(c.isalnum() for c in text):
            continue

        # Drop known garbage tokens
        if text in {"|", "&", "=", "©", "{", "}", "<", ">", "•"}:
            continue

        # Drop layout-only junk
        if all(not c.isalnum() for c in text):
            continue

        filtered.append(b)

    return filtered
