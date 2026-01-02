def merge_bullets(lines):
    merged = []
    buffer = []

    for line in lines:
        if line.startswith(("•", "-", ">")):
            buffer.append(line.lstrip("•-> ").strip())
        else:
            if buffer:
                merged.append(" ".join(buffer))
                buffer = []
            merged.append(line)

    if buffer:
        merged.append(" ".join(buffer))

    return merged
