# omnidoc/core/document.py

from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class Section:
    page: int
    text: str

@dataclass
class Table:
    page: int
    headers: list[str] = field(default_factory=list)
    rows: list[list[str]] = field(default_factory=list)

@dataclass
class Document:
    metadata: dict
    sections: list[Section]
    tables: list[Table]
    raw_text: str = ""
    chunks: list = field(default_factory=list)
