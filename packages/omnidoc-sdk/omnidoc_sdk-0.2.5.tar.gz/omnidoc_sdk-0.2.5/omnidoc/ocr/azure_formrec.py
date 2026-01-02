from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from omnidoc.ocr.base import OCREngine

class AzureFormRecognizer(OCREngine):
    def __init__(self, endpoint, key):
        self.client = DocumentAnalysisClient(
            endpoint, AzureKeyCredential(key)
        )

    def extract(self, file_path: str):
        with open(file_path, "rb") as f:
            poller = self.client.begin_analyze_document(
                "prebuilt-read", f
            )
        result = poller.result()

        pages = []
        for page in result.pages:
            text = "\n".join(line.content for line in page.lines)
            pages.append({"page": page.page_number, "text": text})
        return pages
