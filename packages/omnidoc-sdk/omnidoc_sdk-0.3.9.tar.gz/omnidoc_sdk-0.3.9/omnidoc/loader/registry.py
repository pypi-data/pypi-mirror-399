# omnidoc/loader/registry.py
"""
Central extractor registry.

Rules:
- NEVER instantiate extractors here
- NEVER import loader/router here
- ONLY map extensions → extractor classes
"""

from omnidoc.extractors.text.extractor import TextExtractor
from omnidoc.extractors.office.spreadsheet import SpreadsheetExtractor
from omnidoc.extractors.image.extractor import ImageExtractor
from omnidoc.extractors.code.extractor import CodeExtractor
from omnidoc.extractors.archive.extractor import ArchiveExtractor
from omnidoc.extractors.structured.json_xml import JSONExtractor, XMLExtractor
from omnidoc.extractors.markdown.extractor import MarkdownExtractor
from omnidoc.extractors.docx.extractor import DocxExtractor
from omnidoc.extractors.office.pptx import PPTXExtractor


REGISTRY = {
    # ---------- Text & Docs ----------
    "txt": TextExtractor,
    "md": MarkdownExtractor,
    "rst": TextExtractor,
    "docx": DocxExtractor,
    "odt": TextExtractor,
    "pptx": PPTXExtractor(),
    "ppt": PPTXExtractor(),

    # ---------- Spreadsheets ----------
    "xlsx": SpreadsheetExtractor,
    "xls": SpreadsheetExtractor,
    "csv": SpreadsheetExtractor,
    "tsv": SpreadsheetExtractor,

    # ---------- Images ----------
    "png": ImageExtractor,
    "jpg": ImageExtractor,
    "jpeg": ImageExtractor,
    "tiff": ImageExtractor,

    # ---------- Code ----------
    "py": CodeExtractor,
    "js": CodeExtractor,
    "ts": CodeExtractor,
    "java": CodeExtractor,
    "go": CodeExtractor,
    "sql": CodeExtractor,

    # ---------- Structured ----------
    "json": JSONExtractor,
    "xml": XMLExtractor,
    "yaml": JSONExtractor,
    "yml": JSONExtractor,

    # ---------- Archives ----------
    "zip": ArchiveExtractor,
    "tar": ArchiveExtractor,
    "gz": ArchiveExtractor,
}
