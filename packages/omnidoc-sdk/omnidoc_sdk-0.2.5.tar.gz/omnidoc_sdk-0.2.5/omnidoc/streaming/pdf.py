import pdfplumber

def stream_pdf_pages(path):
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages):
            yield {
                "page": i + 1,
                "text": page.extract_text() or ""
            }
