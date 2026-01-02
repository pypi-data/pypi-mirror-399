from abc import ABC, abstractmethod
from omnidoc.core.document import Document


class BaseExtractor(ABC):
    """
    Abstract base class for all extractors.
    Extractors MUST NOT import loader or router.
    """

    @abstractmethod
    def extract(self, path: str) -> Document:
        raise NotImplementedError
