import logging
import re
from typing import Any

from app.rag.parsers.base import BaseParser

logger = logging.getLogger("zam-ai-core-api.txt-parser")


class TxtParser(BaseParser):
    def parse(self, file_path: str) -> list[dict[str, Any]]:
        """
        Parses a plain text file. It tries to split sections based on headings
        like "1. INTRODUCTION", "CLINICAL GUIDELINE:", etc.
        """
        logger.info(f"Parsing TXT file: {file_path}")
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        sections = []
        
        # Simple heading detection regex: lines that look like "1. HEADING" or ALL CAPS lines
        # or lines starting with numbers and capital letters.
        lines = content.split("\n")
        current_section_title = "Root"
        current_section_text = []
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            
            # Detect section headings like "1. OVERVIEW" or "2. UNCOMPLICATED MALARIA"
            is_heading = re.match(r"^\d+\.\s+[A-Z0-9\s]+$", stripped) or stripped.startswith("CLINICAL GUIDELINE:")
            
            if is_heading:
                # Save previous section if it has content
                if current_section_text:
                    sections.append({
                        "text_content": "\n".join(current_section_text).strip(),
                        "section_path": current_section_title,
                        "page_number": None,
                        "metadata": {"type": "txt_section"}
                    })
                current_section_title = stripped
                current_section_text = [line]
            else:
                current_section_text.append(line)
                
        # Append the final section
        if current_section_text:
            sections.append({
                "text_content": "\n".join(current_section_text).strip(),
                "section_path": current_section_title,
                "page_number": None,
                "metadata": {"type": "txt_section"}
            })

        return sections
