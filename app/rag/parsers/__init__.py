import os

from app.rag.parsers.base import BaseParser
from app.rag.parsers.csv import CsvParser
from app.rag.parsers.json import JsonParser
from app.rag.parsers.pdf import PdfParser
from app.rag.parsers.txt import TxtParser
from app.rag.parsers.xlsx import XlsxParser

_PARSERS: dict[str, type[BaseParser]] = {
    ".pdf": PdfParser,
    ".json": JsonParser,
    ".txt": TxtParser,
    ".csv": CsvParser,
    ".xlsx": XlsxParser,
}


def get_parser(file_path: str) -> BaseParser:
    """
    Returns the appropriate parser instance based on the file extension.
    """
    _, ext = os.path.splitext(file_path.lower())
    parser_class = _PARSERS.get(ext)
    
    if not parser_class:
        raise ValueError(f"No parser registered for file extension: {ext}")
        
    return parser_class()
