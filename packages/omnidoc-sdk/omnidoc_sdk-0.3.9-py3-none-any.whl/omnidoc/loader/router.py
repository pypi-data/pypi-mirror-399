# omnidoc/loader/router.py
from pathlib import Path
from omnidoc.loader.types import DocumentType


def detect_document_type(path: str) -> DocumentType:
    ext = Path(path).suffix.lower().lstrip(".")

    try:
        return DocumentType(ext)
    except ValueError:
        return DocumentType.UNKNOWN
