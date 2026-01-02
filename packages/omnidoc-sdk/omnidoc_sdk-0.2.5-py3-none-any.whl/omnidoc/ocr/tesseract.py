from omnidoc.ocr.base import OCREngine
from pdf2image import convert_from_path
import pytesseract


class TesseractOCR(OCREngine):
    """
    Local OCR engine using Tesseract.
    """

    def extract(self, file_path: str):
        images = convert_from_path(file_path, dpi=300)
        results = []

        for i, image in enumerate(images):
            text = pytesseract.image_to_string(image)
            results.append(
                {
                    "page": i + 1,
                    "text": text,
                    "image": image,
                }
            )

        return results
