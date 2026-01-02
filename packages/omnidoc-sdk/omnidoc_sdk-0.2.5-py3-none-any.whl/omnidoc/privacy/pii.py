def mask_pii(text: str) -> str:
    try:
        from presidio_analyzer import AnalyzerEngine
        from presidio_anonymizer import AnonymizerEngine
    except ImportError as e:
        raise RuntimeError(
            "PII masking requires optional dependency.\n"
            "Install with:\n"
            "  pip install omnidoc-sdk[privacy]"
        ) from e

    analyzer = AnalyzerEngine()
    anonymizer = AnonymizerEngine()

    results = analyzer.analyze(text=text, language="en")
    return anonymizer.anonymize(text, results).text
