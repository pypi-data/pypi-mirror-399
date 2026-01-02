# omnidoc/extractors/image/extractor.py
import pytesseract
from PIL import Image
from omnidoc.extractors.base import BaseExtractor
from omnidoc.core.document import Document, Section


class ImageExtractor(BaseExtractor):
    def extract(self, path: str) -> Document:
        img = Image.open(path)
        text = pytesseract.image_to_string(img)

        return Document(
            metadata={"file": path, "type": "image", "pages": 1},
            sections=[Section(page=1, text=text)],
            raw_text=text
        )
