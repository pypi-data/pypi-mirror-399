# omnidoc/rag/intent.py

import re

def classify_intent(text: str) -> str:
    """
    Classifies chunk intent for agent routing & RAG tuning.
    """

    if re.search(r"\b(benefits|advantages|outcomes)\b", text, re.I):
        return "value_proposition"

    if re.search(r"\b(architecture|workflow|process)\b", text, re.I):
        return "process"

    if re.search(r"\b(roi|%|cost|savings)\b", text, re.I):
        return "metric"

    if text.count("\n") > 5:
        return "detailed_content"

    return "general_content"
