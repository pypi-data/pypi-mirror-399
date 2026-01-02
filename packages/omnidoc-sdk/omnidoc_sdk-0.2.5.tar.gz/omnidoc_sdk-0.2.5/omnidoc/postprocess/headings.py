def is_heading(text: str) -> bool:
    if not text:
        return False

    if text.isupper() and len(text) < 80:
        return True

    if text.endswith(":"):
        return True

    if len(text.split()) <= 6:
        return True

    return False
