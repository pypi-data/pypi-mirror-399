from omnidoc.streaming.pdf import stream_pdf_pages
from omnidoc.utils.text import clean_text
from omnidoc.pdf.normalize import build_document

def extract_pdf_streaming(path: str):
    sections = []

    for page in stream_pdf_pages(path):
        sections.append({
            "page": page["page"],
            "text": clean_text(page["text"])
        })

    return build_document(path, sections, tables=[])
