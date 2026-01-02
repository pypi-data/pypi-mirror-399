import re

INVOICE_PATTERNS = {
    "invoice_number": r"(Invoice\s*(No|Number))[:\s]*([A-Z0-9-]+)",
    "invoice_date": r"(Invoice\s*Date)[:\s]*([\d/-]+)",
    "total_amount": r"(Total\s*(Amount|Due))[:\s]*([$₹€]?\s?\d+[.,]\d+)",
    "gst": r"(GST|VAT)[:\s]*([\d.]+%)"
}

def extract_invoice_kv(text: str) -> dict:
    result = {}
    for key, pattern in INVOICE_PATTERNS.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            result[key] = match.groups()[-1]
    return result
