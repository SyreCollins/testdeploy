"""Ingest all files from the sources/ directory into Pinecone.

Usage:
    python scripts/ingest_sources.py

Run this whenever you add a new source file to the sources/ folder.
Already-ingested files (same checksum) are automatically skipped.
"""
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import get_settings
from app.rag.embeddings.mock import MockEmbeddingProvider
from app.rag.embeddings.voyage import VoyageEmbeddingProvider
from app.rag.registry import RagRegistry
from app.rag.service import IngestionService
from app.rag.vector_store.memory import MemoryVectorStore
from app.rag.vector_store.pinecone import PineconeVectorStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ingest-sources")

SOURCES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sources")

SOURCE_META = {
    "Nigeria-Essential-Medicine-List-2020.pdf": {
        "name": "Nigeria Essential Medicines List",
        "publisher": "Federal Ministry of Health Nigeria",
        "version": "2020",
        "license_status": "active",
        "jurisdiction": "NG",
        "trust_tier": 2,
    },
    "nafdac_products DONE 2.csv": {
        "name": "NAFDAC Registered Products",
        "publisher": "NAFDAC",
        "version": "2024",
        "license_status": "active",
        "jurisdiction": "NG",
        "trust_tier": 3,
    },
    "Medicine_Details.csv": {
        "name": "Medicine Details",
        "publisher": "Various",
        "version": "2024",
        "license_status": "active",
        "jurisdiction": "NG",
        "trust_tier": 3,
    },
    "atc data final.xlsx": {
        "name": "WHO ATC Classification",
        "publisher": "WHO Collaborating Centre",
        "version": "2024",
        "license_status": "active",
        "jurisdiction": "GLOBAL",
        "trust_tier": 2,
    },
}


def main() -> None:
    settings = get_settings()

    registry = RagRegistry(database_url=settings.database_url)
    registry.init_db()

    if settings.voyage_api_key:
        embedding_provider = VoyageEmbeddingProvider(
            api_key=settings.voyage_api_key,
            model=settings.voyage_embedding_model,
        )
        logger.info(f"Using Voyage embedding ({settings.voyage_embedding_model})")
    else:
        embedding_provider = MockEmbeddingProvider()
        logger.warning("No VOYAGE_API_KEY — using mock embeddings (not for production)")

    if settings.pinecone_api_key:
        vector_store = PineconeVectorStore(
            api_key=settings.pinecone_api_key,
            index_name=settings.pinecone_index_name,
        )
        logger.info(f"Using Pinecone index '{settings.pinecone_index_name}'")
    else:
        vector_store = MemoryVectorStore()
        logger.warning("No PINECONE_API_KEY — using in-memory store (data lost on restart)")

    svc = IngestionService(
        registry=registry,
        embedding_provider=embedding_provider,
        vector_store=vector_store,
    )

    if not os.path.isdir(SOURCES_DIR):
        logger.error(f"Sources directory not found: {SOURCES_DIR}")
        sys.exit(1)

    files = sorted(os.listdir(SOURCES_DIR))
    if not files:
        logger.info("No files found in sources/ directory")
        return

    total = 0
    skipped = 0
    for filename in files:
        file_path = os.path.join(SOURCES_DIR, filename)
        if not os.path.isfile(file_path):
            continue

        meta = SOURCE_META.get(filename)
        if not meta:
            logger.warning(f"No metadata mapping for {filename} — skipping")
            continue

        logger.info(f"--- Processing: {filename} ---")
        source = svc.register_source(**meta)

        result = svc.ingest_document(
            source=source,
            file_path=file_path,
            title=filename,
        )

        if result["status"] == "skipped":
            logger.info("  Already ingested, skipped")
            skipped += 1
        else:
            logger.info(f"  Ingested {result['chunks_count']} chunks")
            total += result["chunks_count"]

    logger.info(f"Done — {total} new chunks ingested, {skipped} files already up-to-date")


if __name__ == "__main__":
    main()
