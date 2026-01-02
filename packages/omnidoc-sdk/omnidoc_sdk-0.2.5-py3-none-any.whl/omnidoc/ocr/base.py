from abc import ABC, abstractmethod

class OCREngine(ABC):
    @abstractmethod
    def extract(self, file_path: str) -> list[dict]:
        """Return [{page, text, blocks}]"""
