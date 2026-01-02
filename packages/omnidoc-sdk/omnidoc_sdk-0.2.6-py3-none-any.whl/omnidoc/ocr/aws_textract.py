import boto3
from omnidoc.ocr.base import OCREngine

class TextractOCR(OCREngine):
    def __init__(self, region="us-east-1"):
        self.client = boto3.client("textract", region_name=region)

    def extract(self, file_path: str):
        with open(file_path, "rb") as f:
            document_bytes = f.read()

        response = self.client.analyze_document(
            Document={"Bytes": document_bytes},
            FeatureTypes=["TABLES", "FORMS"]
        )

        pages = {}
        for block in response["Blocks"]:
            if block["BlockType"] == "LINE":
                page = block["Page"]
                pages.setdefault(page, []).append(block["Text"])

        results = []
        for page, lines in pages.items():
            results.append({
                "page": page,
                "text": "\n".join(lines),
                "confidence": sum(
                    b["Confidence"]
                    for b in response["Blocks"]
                    if b.get("Confidence")
                ) / max(len(lines), 1)
            })

        return results
