import pdfplumber
from omnidoc.core.document import Section

def extract_text(path: str) -> list[Section]:
    sections = []
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            sections.append(Section(page=i + 1, text=text))
    return sections
