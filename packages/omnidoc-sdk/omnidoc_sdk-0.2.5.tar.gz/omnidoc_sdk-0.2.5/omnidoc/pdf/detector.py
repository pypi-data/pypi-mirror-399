import pdfplumber

def is_scanned_pdf(path: str) -> bool:
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages[:2]:
            if page.extract_text():
                return False
    return True
