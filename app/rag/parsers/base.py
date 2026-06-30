from abc import ABC, abstractmethod
from typing import Any


class BaseParser(ABC):
    @abstractmethod
    def parse(self, file_path: str) -> list[dict[str, Any]]:
        """
        Parses a document file and returns a list of sections.
        
        Returns:
            list[dict[str, Any]]: A list of dictionaries representing parsed sections.
                Each dict must contain:
                    - "text_content": str (the raw or cleaned text extracted)
                    - "section_path": str (hierarchical path, e.g. "Chapter 1 / Section 2")
                    - "page_number": Optional[int] (the page number if available)
                    - "metadata": dict (additional parser-specific properties)
        """
        pass
