import logging
from datetime import UTC, datetime

from sqlmodel import Session, SQLModel, create_engine, select

from app.core.config import get_settings
from app.rag.schemas import DocumentChunk, MedicalSource, SourceDocument

logger = logging.getLogger("zam-ai-core-api.rag-registry")


class RagRegistry:
    def __init__(self, database_url: str | None = None) -> None:
        settings = get_settings()
        self.database_url = database_url or settings.database_url
        
        # SQLite specific configuration for thread safety
        connect_args = {}
        if self.database_url.startswith("sqlite"):
            connect_args = {"check_same_thread": False}
            
        self.engine = create_engine(self.database_url, connect_args=connect_args)

    def init_db(self) -> None:
        """Create tables in the database if they don't exist"""
        logger.info(f"Initializing RAG registry database at: {self.database_url}")
        SQLModel.metadata.create_all(self.engine)

    def register_source(
        self,
        name: str,
        publisher: str,
        version: str,
        license_status: str,
        jurisdiction: str,
        trust_tier: int | None = None,
        publication_date: str | None = None,
    ) -> MedicalSource:
        """Register a new medical source, or return the existing one if name+version matches"""
        with Session(self.engine) as session:
            statement = select(MedicalSource).where(
                MedicalSource.name == name, MedicalSource.version == version
            )
            existing = session.exec(statement).first()
            if existing:
                return existing

            source = MedicalSource(
                name=name,
                publisher=publisher,
                version=version,
                license_status=license_status,
                jurisdiction=jurisdiction,
                trust_tier=trust_tier,
                publication_date=publication_date,
            )
            session.add(source)
            session.commit()
            session.refresh(source)
            return source

    def register_document(
        self,
        source_id: int,
        title: str,
        file_path: str,
        checksum: str,
        document_version: str | None = None,
    ) -> SourceDocument:
        """Register a new document associated with a medical source"""
        with Session(self.engine) as session:
            statement = select(SourceDocument).where(
                SourceDocument.source_id == source_id,
                SourceDocument.checksum == checksum
            )
            existing = session.exec(statement).first()
            if existing:
                return existing

            doc = SourceDocument(
                source_id=source_id,
                title=title,
                file_path=file_path,
                checksum=checksum,
                document_version=document_version,
                status="pending",
            )
            session.add(doc)
            session.commit()
            session.refresh(doc)
            return doc

    def update_document_status(
        self, document_id: int, status: str, error_message: str | None = None
    ) -> SourceDocument | None:
        """Update the status of a document (e.g. pending, parsed, failed)"""
        with Session(self.engine) as session:
            doc = session.get(SourceDocument, document_id)
            if not doc:
                return None
            
            doc.status = status
            doc.parsed_at = datetime.now(UTC)
            session.add(doc)
            session.commit()
            session.refresh(doc)
            return doc

    def add_chunks(self, chunks: list[DocumentChunk]) -> None:
        """Batch insert chunks into the registry"""
        with Session(self.engine) as session:
            for chunk in chunks:
                # Merge checks if it exists, otherwise inserts
                session.merge(chunk)
            session.commit()

    def get_source(self, source_id: int) -> MedicalSource | None:
        """Fetch a source by its ID."""
        with Session(self.engine) as session:
            return session.get(MedicalSource, source_id)

    def get_chunks_for_document(self, document_id: int) -> list[DocumentChunk]:
        """Get all chunks associated with a document"""
        with Session(self.engine) as session:
            statement = select(DocumentChunk).where(DocumentChunk.document_id == document_id)
            return list(session.exec(statement).all())

    def get_source_metadata_for_chunk(self, chunk_id: str) -> dict | None:
        """
        Retrieve chunk information along with the document and source metadata
        essential for generating grounded citations.
        """
        with Session(self.engine) as session:
            # Fetch chunk
            chunk = session.get(DocumentChunk, chunk_id)
            if not chunk:
                return None
            
            # Fetch document
            doc = session.get(SourceDocument, chunk.document_id)
            if not doc:
                return None
                
            # Fetch source
            source = session.get(MedicalSource, doc.source_id)
            if not source:
                return None
                
            return {
                "chunk_id": chunk.id,
                "text_content": chunk.text_content,
                "section_path": chunk.section_path,
                "page_number": chunk.page_number,
                "document_title": doc.title,
                "source_name": source.name,
                "source_version": source.version,
                "publisher": source.publisher,
                "jurisdiction": source.jurisdiction,
            }
