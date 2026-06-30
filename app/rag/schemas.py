from datetime import UTC, datetime

from sqlmodel import Field, Relationship, SQLModel


class MedicalSource(SQLModel, table=True):
    __tablename__ = "medical_sources"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    publisher: str
    version: str
    license_status: str  # e.g., "active", "expired", "pending"
    jurisdiction: str  # e.g., "NG", "UK", "GLOBAL"
    publication_date: str | None = None
    ingested_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationships
    documents: list["SourceDocument"] = Relationship(back_populates="source")


class SourceDocument(SQLModel, table=True):
    __tablename__ = "source_documents"

    id: int | None = Field(default=None, primary_key=True)
    source_id: int = Field(foreign_key="medical_sources.id", index=True)
    title: str
    file_path: str
    checksum: str
    document_version: str | None = None
    parsed_at: datetime | None = None
    status: str = Field(default="pending")  # "pending", "parsed", "failed"

    # Relationships
    source: MedicalSource = Relationship(back_populates="documents")
    chunks: list["DocumentChunk"] = Relationship(back_populates="document")


class DocumentChunk(SQLModel, table=True):
    __tablename__ = "document_chunks"

    # id should be a string (e.g. UUID or hash-based) since it matches vector IDs in Pinecone
    id: str = Field(primary_key=True)
    document_id: int = Field(foreign_key="source_documents.id", index=True)
    chunk_type: str  # e.g. "dosage", "contraindication", "general"
    section_path: str
    page_number: int | None = None
    text_content: str
    embedding_id: str | None = None
    
    # Medical entity linking
    generic_name: str | None = Field(default=None, index=True)
    brand_names: str | None = None  # Comma-separated or JSON list of brands

    # Relationships
    document: SourceDocument = Relationship(back_populates="chunks")


class Citation(SQLModel):
    """
    Non-table schema returned to backend/users representing the grounded citation
    """
    citation_id: str
    source_name: str
    source_version: str
    document_title: str
    section_path: str
    page_number: int | None = None
    text_content: str
