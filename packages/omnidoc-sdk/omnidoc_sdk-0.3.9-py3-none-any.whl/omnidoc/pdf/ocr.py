from pdf2image import convert_from_path
import pytesseract
from omnidoc.core.document import Section

def ocr_pdf(path: str) -> list[Section]:
    images = convert_from_path(path, dpi=300)
    sections = []

    for i, img in enumerate(images):
        text = pytesseract.image_to_string(img)
        sections.append(Section(page=i + 1, text=text))

    return sections
