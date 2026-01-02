# omnidoc/loader/load.py

from omnidoc.loader.router import detect_document_type
from omnidoc.loader.types import DocumentType
from omnidoc.pdf.pipeline import extract_pdf


def load_document(
    path: str,
    *,
    enable_semantic_chunks: bool = True,
    **pdf_options,
):
    """
    Universal document loader.
    Applies semantic chunking for ALL document types.
    """

    doc_type = detect_document_type(path)

    # -----------------------------
    # PDF → Pipeline
    # -----------------------------
    if doc_type == DocumentType.PDF:
        doc = extract_pdf(
            path,
            enable_semantic_chunks=False,  # IMPORTANT
            **pdf_options,
        )

    # -----------------------------
    # Non-PDF → Extractors
    # -----------------------------
    else:
        doc = _load_non_pdf(path, doc_type)

    # -----------------------------
    # 🔥 SEMANTIC CHUNKING (GLOBAL)
    # -----------------------------
    if enable_semantic_chunks:
        from omnidoc.rag.semantic_chunker import semantic_chunk_document
        doc.chunks = semantic_chunk_document(doc)
    else:
        doc.chunks = []

    return doc


def _load_non_pdf(path: str, doc_type: DocumentType):
    """
    Lazy extractor resolution.
    """

    if doc_type == DocumentType.TXT:
        from omnidoc.extractors.text.extractor import TextExtractor
        return TextExtractor().extract(path)

    if doc_type == DocumentType.MD:
        from omnidoc.extractors.markdown.extractor import MarkdownExtractor
        return MarkdownExtractor().extract(path)

    if doc_type == DocumentType.DOCX:
        from omnidoc.extractors.office.docx import DocxExtractor
        return DocxExtractor().extract(path)

    if doc_type in (DocumentType.XLSX, DocumentType.CSV):
        from omnidoc.extractors.office.spreadsheet import SpreadsheetExtractor
        return SpreadsheetExtractor().extract(path)

    if doc_type == DocumentType.PPTX:
        from omnidoc.extractors.office.pptx import PPTXExtractor
        return PPTXExtractor().extract(path)

    if doc_type in (DocumentType.PNG, DocumentType.JPG, DocumentType.JPEG):
        from omnidoc.extractors.image.extractor import ImageExtractor
        return ImageExtractor().extract(path)

    if doc_type == DocumentType.JSON:
        from omnidoc.extractors.structured.json_xml import JSONExtractor
        return JSONExtractor().extract(path)

    if doc_type == DocumentType.ZIP:
        from omnidoc.extractors.archive.extractor import ArchiveExtractor
        return ArchiveExtractor().extract(path)

    raise ValueError(f"Unsupported document type: {doc_type}")
