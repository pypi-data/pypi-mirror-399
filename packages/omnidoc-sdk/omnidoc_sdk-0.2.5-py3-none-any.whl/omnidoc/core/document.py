from dataclasses import dataclass, field

@dataclass
class Table:
    page: int
    headers: list[str]
    rows: list[list[str]]

@dataclass
class Section:
    page: int
    text: str

@dataclass
class Document:
    metadata: dict
    sections: list[Section] = field(default_factory=list)
    tables: list[Table] = field(default_factory=list)
    raw_text: str = ""
