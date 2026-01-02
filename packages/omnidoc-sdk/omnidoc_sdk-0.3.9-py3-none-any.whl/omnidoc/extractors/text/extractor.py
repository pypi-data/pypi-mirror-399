from omnidoc.core.document import Document, Section, Table

class TextExtractor:
    def extract(self, path: str) -> Document:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        sections = [
            Section(page=1, text=text)
        ]

        return Document(
            metadata={
                "file": path,
                "pages": 1,
                "type": "text"
            },
            sections=sections,   # ✅ FIXED
            tables=[],           # ✅ REQUIRED
            raw_text=text
        )
