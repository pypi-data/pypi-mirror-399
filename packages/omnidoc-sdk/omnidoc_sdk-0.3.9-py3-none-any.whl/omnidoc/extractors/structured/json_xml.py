# omnidoc/extractors/structured/json_xml.py
import json
import xml.etree.ElementTree as ET
from omnidoc.extractors.base import BaseExtractor
from omnidoc.core.document import Document, Section


class JSONExtractor(BaseExtractor):
    """
    Extract structured JSON documents.
    """

    def extract(self, path: str) -> Document:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        text = json.dumps(data, indent=2)

        return Document(
            metadata={
                "file": path,
                "type": "json",
                "pages": 1,
            },
            sections=[
                Section(page=1, text=text)
            ],
            raw_text=text,
        )


class XMLExtractor(BaseExtractor):
    """
    Extract XML documents.
    """

    def extract(self, path: str) -> Document:
        tree = ET.parse(path)
        root = tree.getroot()

        def flatten(elem, depth=0):
            lines = []
            indent = "  " * depth
            lines.append(f"{indent}<{elem.tag}>")

            for child in elem:
                lines.extend(flatten(child, depth + 1))

            return lines

        lines = flatten(root)
        text = "\n".join(lines)

        return Document(
            metadata={
                "file": path,
                "type": "xml",
                "pages": 1,
            },
            sections=[
                Section(page=1, text=text)
            ],
            raw_text=text,
        )
