# omnidoc/rag/confidence.py

def score_chunk(text: str) -> float:
    """
    Deterministic confidence scoring (no ML).
    """

    score = 1.0

    if len(text) < 100:
        score -= 0.3

    if not any(c.isdigit() for c in text):
        score -= 0.1

    if text.count("\n") < 2:
        score -= 0.1

    return round(max(score, 0.1), 2)
