import re
from typing import Any

# Basic dictionary mapping common brand names to generic names for resolution
BRAND_TO_GENERIC = {
    "augmentin": "amoxicillin/clavulanate",
    "amoxil": "amoxicillin",
    "moxatag": "amoxicillin",
    "advil": "ibuprofen",
    "motrin": "ibuprofen",
    "nurofen": "ibuprofen",
    "coartem": "artemether/lumefantrine",
}

# Known drugs to scan for entity linking
KNOWN_DRUGS = [
    "amoxicillin",
    "clavulanate",
    "ibuprofen",
    "artemether",
    "lumefantrine",
    "warfarin",
    "aspirin",
    "paracetamol",
]


def clean_whitespace(text: str) -> str:
    """
    Cleans multiple spaces, tabs, and duplicate blank lines while preserving structure.
    """
    if not text:
        return ""
    # Replace multiple spaces with a single space
    text = re.sub(r"[ \t]+", " ", text)
    # Replace 3 or more newlines with double newlines (to preserve paragraphs)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def normalize_drug_name(name: str) -> str:
    """
    Converts drug names to lowercase and resolves brand names to generic names where possible.
    """
    if not name:
        return ""
    cleaned = name.strip().lower()
    return BRAND_TO_GENERIC.get(cleaned, cleaned)


def extract_medications(text: str) -> dict[str, Any]:
    """
    Scans text content for known medications and maps any found brand names and generic names.
    
    Returns a dict with:
        - "generic_name": Optional[str] (resolved generic name)
        - "brand_names": List[str] (list of brand names found)
    """
    found_brands = []
    found_generics = []
    
    text_lower = text.lower()
    
    # Check brand names
    for brand, generic in BRAND_TO_GENERIC.items():
        if re.search(r'\b' + re.escape(brand) + r'\b', text_lower):
            found_brands.append(brand.capitalize())
            found_generics.append(generic)
            
    # Check direct generic names
    for generic in KNOWN_DRUGS:
        if re.search(r'\b' + re.escape(generic) + r'\b', text_lower):
            found_generics.append(generic)
            
    # Deduplicate generics list
    found_generics = list(set(found_generics))
    found_brands = list(set(found_brands))
    
    return {
        "generic_name": found_generics[0].capitalize() if found_generics else None,
        "brand_names": found_brands,
    }


def normalize_dosage_units(text: str) -> str:
    """
    Standardizes spelling of common dosage units to prevent confusion.
    e.g., milligram -> mg, microgram -> mcg
    """
    if not text:
        return ""
    
    # Map full names to abbreviations safely
    text = re.sub(r"\bmilligrams?\b", "mg", text, flags=re.IGNORECASE)
    text = re.sub(r"\bmicrograms?\b", "mcg", text, flags=re.IGNORECASE)
    text = re.sub(r"\bgrams?\b", "g", text, flags=re.IGNORECASE)
    text = re.sub(r"\bmilliliters?\b", "mL", text, flags=re.IGNORECASE)
    
    return text
