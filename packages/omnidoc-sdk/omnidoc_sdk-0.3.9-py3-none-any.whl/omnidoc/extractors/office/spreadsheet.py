# omnidoc/extractors/office/spreadsheet.py
import pandas as pd
from omnidoc.extractors.base import BaseExtractor
from omnidoc.core.document import Document, Table


class SpreadsheetExtractor(BaseExtractor):
    def extract(self, path: str) -> Document:
        df = pd.read_excel(path) if path.endswith("xlsx") else pd.read_csv(path)

        table = Table(
            page=1,
            headers=list(df.columns),
            rows=df.astype(str).values.tolist()
        )

        return Document(
            metadata={"file": path, "type": "spreadsheet", "pages": 1},
            tables=[table],
            raw_text=df.to_string()
        )
