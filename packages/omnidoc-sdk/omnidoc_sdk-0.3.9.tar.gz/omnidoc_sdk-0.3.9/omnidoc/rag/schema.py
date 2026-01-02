from dataclasses import dataclass
from typing import Optional, Dict


@dataclass
class SemanticChunk:
    id: str
    text: str
    section: Optional[str]
    page_start: int
    page_end: int
    intent: str  # narrative | metric | table | heading
    metadata: Dict
