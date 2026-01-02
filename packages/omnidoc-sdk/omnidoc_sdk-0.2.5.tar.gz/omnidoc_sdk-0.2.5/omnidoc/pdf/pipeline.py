# -------------------------------------------------
# Safe warning & log suppression (SDK-level)
# -------------------------------------------------
import warnings
import logging
from typing import Optional, Dict, Any, Union

warnings.filterwarnings("ignore")
logging.getLogger("pdfminer").setLevel(logging.CRITICAL)
logging.getLogger("pdfplumber").setLevel(logging.CRITICAL)
logging.getLogger("pypdf").setLevel(logging.CRITICAL)

# -------------------------------------------------

from omnidoc.pdf.detector import is_scanned_pdf
from omnidoc.pdf.text import extract_text
from omnidoc.pdf.tables import extract_tables
from omnidoc.pdf.ocr_tables import extract_ocr_tables
from omnidoc.pdf.normalize import build_document

from omnidoc.ocr.base import OCREngine
from omnidoc.ocr.tesseract import TesseractOCR

from omnidoc.utils.text import clean_text
from omnidoc.layout.ordering import order_blocks
from omnidoc.layout.utils import text_blocks_only


def extract_pdf(
    path: str,
    *,
    ocr_engine: Optional[OCREngine] = None,
    enable_layout: bool = True,
    enable_pii_masking: bool = False,
    enable_cloud_ocr: bool = False,
    enable_vlm: bool = False,
    output_format: str = "document",  # document | json | toon
) -> Union[Dict[str, Any], object]:
    """
    Enterprise-grade PDF extraction pipeline.

    Supports:
    - Digital PDFs
    - Slide / brochure PDFs
    - Scanned PDFs
    - OCR + Layout ML
    - Slide → report normalization
    - JSON / TOON output
    """

    sections: list[dict] = []
    tables: list[dict] = []

    scanned = is_scanned_pdf(path)

    # -------------------------------------------------
    # OCR routing
    # -------------------------------------------------
    if scanned and enable_cloud_ocr:
        from omnidoc.ocr.aws_textract import TextractOCR
        ocr_engine = TextractOCR()
    else:
        ocr_engine = ocr_engine or TesseractOCR()

    # =================================================
    # 1️⃣ DIGITAL PDF — SIMPLE
    # =================================================
    if not scanned and not enable_layout:
        for sec in extract_text(path):
            sections.append({
                "page": sec["page"],
                "text": clean_text(sec["text"]),
            })

        tables = extract_tables(path)

    # =================================================
    # 2️⃣ DIGITAL PDF — LAYOUT AWARE (slides / decks)
    # =================================================
    elif not scanned and enable_layout:
        from pdf2image import convert_from_path
        from omnidoc.layout.detector import detect_layout
        import pytesseract

        images = convert_from_path(path, dpi=250)

        for i, image in enumerate(images):
            text = ""

            blocks = detect_layout(image)
            if blocks:
                blocks = order_blocks(text_blocks_only(blocks))
                text = "\n".join(b.text for b in blocks)

            # OCR fallback only if layout failed
            if not text.strip():
                text = pytesseract.image_to_string(image)

            sections.append({
                "page": i + 1,
                "text": clean_text(text),
            })

            ocr_tables = extract_ocr_tables(image)
            if ocr_tables:
                tables.append({
                    "page": i + 1,
                    "rows": ocr_tables,
                })

    # =================================================
    # 3️⃣ SCANNED PDF
    # =================================================
    else:
        import pytesseract
        from omnidoc.layout.detector import detect_layout

        for page in ocr_engine.extract(path):
            text = page.get("text", "")

            if enable_vlm and "image" in page:
                from omnidoc.layout.donut import DonutExtractor
                text = DonutExtractor().extract(page["image"])

            elif enable_layout and "image" in page:
                blocks = detect_layout(page["image"])
                if blocks:
                    blocks = order_blocks(text_blocks_only(blocks))
                    text = "\n".join(b.text for b in blocks)
                else:
                    text = pytesseract.image_to_string(page["image"])

                ocr_tables = extract_ocr_tables(page["image"])
                if ocr_tables:
                    tables.append({
                        "page": page["page"],
                        "rows": ocr_tables,
                    })

            sections.append({
                "page": page["page"],
                "text": clean_text(text),
            })

    # =================================================
    # BUILD DOCUMENT
    # =================================================
    doc = build_document(path, sections, tables)

    # =================================================
    # SLIDE → REPORT NORMALIZATION (NO DECORATORS)
    # =================================================
    from omnidoc.postprocess.slide_normalizer import normalize_slide_sections

    doc.sections = normalize_slide_sections(doc.sections)
    doc.raw_text = "\n\n".join(sec.text for sec in doc.sections)

    # -------------------------------------------------
    # PII masking
    # -------------------------------------------------
    if enable_pii_masking:
        from omnidoc.privacy.pii import mask_pii
        doc.raw_text = mask_pii(doc.raw_text)

    # =================================================
    # OUTPUT FORMAT
    # =================================================
    from omnidoc.utils.serialize import document_to_json, document_to_toon

    if output_format == "json":
        return document_to_json(doc)

    if output_format == "toon":
        return document_to_toon(doc)

    return doc
