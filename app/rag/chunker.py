import hashlib
import logging
from typing import Any

from app.rag.normalizer import (
    clean_whitespace,
    extract_medications,
    normalize_dosage_units,
)
from app.db.models.rag import DocumentChunk

logger = logging.getLogger("zam-ai-core-api.chunker")


class Chunker:
    def __init__(self, max_chunk_chars: int = 1000, overlap_chars: int = 150) -> None:
        self.max_chunk_chars = max_chunk_chars
        self.overlap_chars = overlap_chars

    def chunk_section(self, section: dict[str, Any], document_id: int) -> list[DocumentChunk]:
        """
        Chunks a parsed section dictionary, normalizes its content, 
        and extracts drug metadata to associate with each chunk.
        """
        raw_text = section.get("text_content", "")
        cleaned_text = clean_whitespace(raw_text)
        cleaned_text = normalize_dosage_units(cleaned_text)

        if not cleaned_text:
            return []

        section_path = section.get("section_path", "Unknown")
        page_number = section.get("page_number")
        
        # Determine medication info from parser metadata or fallback to extraction
        metadata = section.get("metadata", {})
        generic_name = metadata.get("generic_name")
        brand_names_list = metadata.get("brand_names", [])
        chunk_type = metadata.get("chunk_type", "general")

        if not generic_name:
            extracted = extract_medications(cleaned_text)
            generic_name = extracted.get("generic_name")
            brand_names_list = extracted.get("brand_names", [])

        brand_names = ",".join(brand_names_list) if brand_names_list else None

        # Split text into segments if it exceeds max size
        text_segments = self._split_text(cleaned_text)

        chunks = []
        for index, segment in enumerate(text_segments):
            # Generate a unique stable ID for this chunk
            chunk_hash = hashlib.sha256(
                f"{document_id}_{section_path}_{page_number}_{index}_{segment}".encode()
            ).hexdigest()

            chunk = DocumentChunk(
                id=f"chk_{chunk_hash[:16]}",
                document_id=document_id,
                chunk_type=chunk_type,
                section_path=section_path,
                page_number=page_number,
                text_content=segment,
                generic_name=generic_name,
                brand_names=brand_names,
            )
            chunks.append(chunk)

        return chunks

    def _split_text(self, text: str) -> list[str]:
        """
        Splits text into chunks of maximum character size with overlap.
        Preserves paragraph and sentence boundaries where possible.
        """
        if len(text) <= self.max_chunk_chars:
            return [text]

        # Simple splitting logic by paragraphs first, then sentences, then character count
        paragraphs = text.split("\n\n")
        chunks = []
        current_chunk = ""

        for para in paragraphs:
            if len(para) > self.max_chunk_chars:
                # If a single paragraph is too large, split it by sentence
                sentences = re_split_sentences(para)
                for sentence in sentences:
                    if len(current_chunk) + len(sentence) + 1 > self.max_chunk_chars:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = sentence + " "
                    else:
                        current_chunk += sentence + " "
            else:
                if len(current_chunk) + len(para) + 2 > self.max_chunk_chars:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = para + "\n\n"
                else:
                    current_chunk += para + "\n\n"

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks


def re_split_sentences(text: str) -> list[str]:
    """Helper to split text by sentences using a regex pattern"""
    sentence_end = re_compile_sentence_split()
    sentences = sentence_end.split(text)
    
    result = []
    # Reassemble split sentences (since split drops the punctuation)
    for i in range(0, len(sentences) - 1, 2):
        result.append(sentences[i] + sentences[i+1])
    if len(sentences) % 2 != 0:
        result.append(sentences[-1])
        
    return [s.strip() for s in result if s.strip()]


# Cached regexes to avoid re-compilation
_sent_split_regex = None

def re_compile_sentence_split():
    global _sent_split_regex
    import re
    if _sent_split_regex is None:
        _sent_split_regex = re.compile(r"([.!?]\s+)")
    return _sent_split_regex
