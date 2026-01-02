# omnidoc/extractors/code/extractor.py
from omnidoc.extractors.base import BaseExtractor
from omnidoc.core.document import Document, Section


class CodeExtractor(BaseExtractor):
    def extract(self, path: str) -> Document:
        with open(path, "r", errors="ignore") as f:
            code = f.read()

        return Document(
            metadata={"file": path, "type": "code", "pages": 1},
            sections=[Section(page=1, text=code)],
            raw_text=code
        )
