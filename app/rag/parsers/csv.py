import csv
import logging
import re
from typing import Any

from app.rag.parsers.base import BaseParser

logger = logging.getLogger("zam-ai-core-api.csv-parser")


class CsvParser(BaseParser):
    def parse(self, file_path: str) -> list[dict[str, Any]]:
        logger.info(f"Parsing CSV file: {file_path}")
        rows = self._read_csv_with_encoding(file_path)

        if not rows:
            return []

        headers = list(rows[0].keys())
        headers_lower = [h.lower().strip() for h in headers]

        if self._is_medicine_details(headers_lower):
            return self._parse_medicine_details(rows, headers)
        if self._is_nafdac_products(headers_lower):
            return self._parse_nafdac_products(rows, headers)
        return self._parse_generic_rows(rows, headers)

    @staticmethod
    def _read_csv_with_encoding(file_path: str) -> list[dict[str, str]]:
        encodings = ["utf-8-sig", "cp1252", "latin-1"]
        for enc in encodings:
            try:
                with open(file_path, encoding=enc) as f:
                    reader = csv.DictReader(f)
                    return list(reader)
            except (UnicodeDecodeError, UnicodeError):
                continue
        msg = f"Could not decode CSV file: {file_path}"
        raise ValueError(msg)

    def _is_medicine_details(self, headers: list[str]) -> bool:
        return "medicine name" in headers and "composition" in headers

    def _is_nafdac_products(self, headers: list[str]) -> bool:
        return "nafdacnumber" in headers or "nafdac_number" in headers

    def _parse_medicine_details(
        self, rows: list[dict[str, str]], headers: list[str]
    ) -> list[dict[str, Any]]:
        sections = []
        for row in rows:
            medicine_name = row.get("Medicine Name", "").strip()
            if not medicine_name:
                continue
            composition = row.get("Composition", "").strip()
            uses = row.get("Uses", "").strip()
            side_effects = row.get("Side_effects", row.get("Side effects", "")).strip()
            manufacturer = row.get("Manufacturer", "").strip()

            generic_name = self._extract_generic_from_composition(composition) or medicine_name
            brand_names = [medicine_name]

            sections.append({
                "text_content": (
                    f"Medication: {medicine_name}\n"
                    f"Composition: {composition}\n"
                    f"Manufacturer: {manufacturer}"
                ),
                "section_path": f"{medicine_name} / Overview",
                "page_number": None,
                "metadata": {
                    "generic_name": generic_name,
                    "brand_names": brand_names,
                    "chunk_type": "overview",
                },
            })
            if uses:
                uses_text = "\n".join(f"- {u.strip()}" for u in re.split(r"(?:^|\s)(?=[A-Z])", uses) if u.strip())
                sections.append({
                    "text_content": f"Uses of {medicine_name}:\n{uses_text}",
                    "section_path": f"{medicine_name} / Uses",
                    "page_number": None,
                    "metadata": {
                        "generic_name": generic_name,
                        "brand_names": brand_names,
                        "chunk_type": "indication",
                    },
                })
            if side_effects:
                se_list = [s.strip() for s in re.split(r"(?<=[a-z])(?=[A-Z])", side_effects) if s.strip()]
                se_text = "\n".join(f"- {s}" for s in se_list)
                sections.append({
                    "text_content": f"Side Effects of {medicine_name}:\n{se_text}",
                    "section_path": f"{medicine_name} / Side Effects",
                    "page_number": None,
                    "metadata": {
                        "generic_name": generic_name,
                        "brand_names": brand_names,
                        "chunk_type": "side_effect",
                    },
                })
        return sections

    def _parse_nafdac_products(
        self, rows: list[dict[str, str]], headers: list[str]
    ) -> list[dict[str, Any]]:
        sections = []
        for row in rows:
            name = row.get("name", "").strip()
            if not name:
                continue
            generic_name = row.get("genericname", "").strip() or name
            strength = row.get("strength", "").strip()
            form = row.get("form", "").strip()
            nafdac_number = row.get("nafdacnumber", "").strip()
            atc_code = row.get("atccode", "").strip()
            manufacturer = row.get("Manufacturer", "").strip()
            description = row.get("description", "").strip()
            tags = row.get("tags", "").strip()
            unitsize = row.get("unitsize", "").strip()

            details = f"Medication: {name}"
            if generic_name and generic_name.lower() != name.lower():
                details += f"\nGeneric Name: {generic_name}"
            if strength:
                details += f"\nStrength: {strength}"
            if form:
                details += f"\nForm: {form}"
            if manufacturer:
                details += f"\nManufacturer: {manufacturer}"
            if nafdac_number:
                details += f"\nNAFDAC Number: {nafdac_number}"
            if atc_code:
                details += f"\nATC Code: {atc_code}"
            if unitsize:
                details += f"\nUnit Size: {unitsize}"

            sections.append({
                "text_content": details,
                "section_path": f"{name} / Overview",
                "page_number": None,
                "metadata": {
                    "generic_name": generic_name,
                    "brand_names": [name],
                    "chunk_type": "overview",
                },
            })
            if tags:
                sections.append({
                    "text_content": f"Tags for {name}: {tags}",
                    "section_path": f"{name} / Tags",
                    "page_number": None,
                    "metadata": {
                        "generic_name": generic_name,
                        "brand_names": [name],
                        "chunk_type": "general",
                    },
                })
            if description:
                sections.append({
                    "text_content": f"Description of {name}:\n{description}",
                    "section_path": f"{name} / Description",
                    "page_number": None,
                    "metadata": {
                        "generic_name": generic_name,
                        "brand_names": [name],
                        "chunk_type": "general",
                    },
                })
        return sections

    def _parse_generic_rows(
        self, rows: list[dict[str, str]], headers: list[str]
    ) -> list[dict[str, Any]]:
        sections = []
        for index, row in enumerate(rows):
            text_parts = [f"{k}: {v}" for k, v in row.items() if v and v.strip()]
            if not text_parts:
                continue
            sections.append({
                "text_content": "\n".join(text_parts),
                "section_path": f"Row {index}",
                "page_number": None,
                "metadata": {"type": "csv_row"},
            })
        return sections

    @staticmethod
    def _extract_generic_from_composition(composition: str) -> str | None:
        match = re.match(r"^([A-Za-z]+)", composition.strip())
        if match:
            return match.group(1).lower().capitalize()
        return None
