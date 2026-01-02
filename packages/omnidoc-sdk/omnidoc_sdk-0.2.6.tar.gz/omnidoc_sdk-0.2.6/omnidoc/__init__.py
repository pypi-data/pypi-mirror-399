__all__ = ["extract_pdf"]

def extract_pdf(*args, **kwargs):
    from omnidoc.pdf.pipeline import extract_pdf as _extract_pdf
    return _extract_pdf(*args, **kwargs)
