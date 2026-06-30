import json
import logging
from typing import Any

from app.rag.parsers.base import BaseParser

logger = logging.getLogger("zam-ai-core-api.json-parser")


class JsonParser(BaseParser):
    def parse(self, file_path: str) -> list[dict[str, Any]]:
        """
        Parses a JSON file. If it detects a list of structured drug definitions,
        it parses it into section-specific text contents for RAG chunking.
        """
        logger.info(f"Parsing JSON file: {file_path}")
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)

        sections = []

        if isinstance(data, list):
            # Attempt to parse as list of structured drug records
            for index, item in enumerate(data):
                if isinstance(item, dict) and "generic_name" in item:
                    sections.extend(self._parse_drug_item(item, index))
                else:
                    sections.append({
                        "text_content": json.dumps(item, indent=2),
                        "section_path": f"Item {index}",
                        "page_number": None,
                        "metadata": {"type": "generic_json"}
                    })
        elif isinstance(data, dict):
            # Parse top-level keys as sections
            for key, val in data.items():
                sections.append({
                    "text_content": val if isinstance(val, str) else json.dumps(val, indent=2),
                    "section_path": key,
                    "page_number": None,
                    "metadata": {"type": "generic_json"}
                })
        else:
            sections.append({
                "text_content": str(data),
                "section_path": "Root",
                "page_number": None,
                "metadata": {"type": "generic_json"}
            })

        return sections

    def _parse_drug_item(self, item: dict[str, Any], index: int) -> list[dict[str, Any]]:
        sections = []
        generic_name = item.get("generic_name", "Unknown")
        brand_names = item.get("brand_names", [])

        # Overview Section
        overview = f"Medication: {generic_name}\n"
        if brand_names:
            overview += f"Brand Names: {', '.join(brand_names)}\n"
        if "atc_code" in item:
            overview += f"ATC Code: {item['atc_code']}\n"
        
        sections.append({
            "text_content": overview.strip(),
            "section_path": f"{generic_name} / Overview",
            "page_number": None,
            "metadata": {
                "generic_name": generic_name,
                "brand_names": brand_names,
                "chunk_type": "overview",
            }
        })

        # Indications
        if "indications" in item:
            ind_text = "\n".join([f"- {ind}" for ind in item["indications"]])
            sections.append({
                "text_content": f"Indications for {generic_name}:\n{ind_text}",
                "section_path": f"{generic_name} / Indications",
                "page_number": None,
                "metadata": {
                    "generic_name": generic_name,
                    "brand_names": brand_names,
                    "chunk_type": "indication",
                }
            })

        # Contraindications
        if "contraindications" in item:
            contra_text = "\n".join([f"- {c}" for c in item["contraindications"]])
            sections.append({
                "text_content": f"Contraindications for {generic_name}:\n{contra_text}",
                "section_path": f"{generic_name} / Contraindications",
                "page_number": None,
                "metadata": {
                    "generic_name": generic_name,
                    "brand_names": brand_names,
                    "chunk_type": "contraindication",
                }
            })

        # Warnings
        if "warnings" in item:
            warn_text = "\n".join([f"- {w}" for w in item["warnings"]])
            sections.append({
                "text_content": f"Warnings for {generic_name}:\n{warn_text}",
                "section_path": f"{generic_name} / Warnings",
                "page_number": None,
                "metadata": {
                    "generic_name": generic_name,
                    "brand_names": brand_names,
                    "chunk_type": "warning",
                }
            })

        # Side Effects
        if "side_effects" in item:
            se_text = "\n".join([f"- {se}" for se in item["side_effects"]])
            sections.append({
                "text_content": f"Side Effects for {generic_name}:\n{se_text}",
                "section_path": f"{generic_name} / Side Effects",
                "page_number": None,
                "metadata": {
                    "generic_name": generic_name,
                    "brand_names": brand_names,
                    "chunk_type": "side_effect",
                }
            })

        # Dosage Guidance
        if "dosage_guidance" in item:
            sections.append({
                "text_content": f"Dosage Guidance for {generic_name}:\n{item['dosage_guidance']}",
                "section_path": f"{generic_name} / Dosage",
                "page_number": None,
                "metadata": {
                    "generic_name": generic_name,
                    "brand_names": brand_names,
                    "chunk_type": "dosage",
                }
            })

        return sections
