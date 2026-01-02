# omnidoc/rag/adaptive.py

INTENT_TOKEN_LIMITS = {
    "metric": 200,
    "value_proposition": 250,
    "process": 350,
    "detailed_content": 450,
    "general_content": 300,
}

DEFAULT_TOKENS = 300


def tokens_for_intent(intent: str) -> int:
    """
    Adaptive chunk sizing based on semantic intent.
    """
    return INTENT_TOKEN_LIMITS.get(intent, DEFAULT_TOKENS)
