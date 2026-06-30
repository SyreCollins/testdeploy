import logging
from typing import Any

from pypdf import PdfReader

from app.rag.parsers.base import BaseParser

logger = logging.getLogger("zam-ai-core-api.pdf-parser")


class PdfParser(BaseParser):
    def parse(self, file_path: str) -> list[dict[str, Any]]:
        """
        Parses a PDF file page-by-page, extracting text and metadata.
        """
        logger.info(f"Parsing PDF file: {file_path}")
        reader = PdfReader(file_path)
        sections = []

        for index, page in enumerate(reader.pages):
            page_number = index + 1
            text = page.extract_text()
            if not text or not text.strip():
                continue

            # Check if there are obvious headings on the page to build section paths
            # (In a production system, we would use layout parser or section detection).
            # For the MVP, we designate the page number as the hierarchical path.
            sections.append({
                "text_content": text,
                "section_path": f"Page {page_number}",
                "page_number": page_number,
                "metadata": {
                    "total_pages": len(reader.pages)
                }
            })

        return sections
