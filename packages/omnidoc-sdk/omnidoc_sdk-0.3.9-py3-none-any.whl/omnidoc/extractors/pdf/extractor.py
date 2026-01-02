from omnidoc.extractors.base import BaseExtractor
from omnidoc.pdf.pipeline import extract_pdf


class PDFExtractor(BaseExtractor):
    """
    Delegates to the PDF pipeline.
    """

    def extract(self, path: str):
        return extract_pdf(
            path,
            enable_layout=True,
            enable_cloud_ocr=True,
            enable_semantic_chunks=True,
        )
