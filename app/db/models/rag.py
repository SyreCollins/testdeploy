from datetime import UTC, datetime

from sqlmodel import Field, Relationship, SQLModel


class MedicalSource(SQLModel, table=True):
    __tablename__ = "medical_sources"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    publisher: str
    version: str
    license_status: str
    jurisdiction: str
    trust_tier: int | None = Field(default=None, description="1=EMDEX, 2=WHO ATC/EML, 3=NAFDAC, 4=BNF/MIMS")
    publication_date: str | None = None
    ingested_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

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
    status: str = Field(default="pending")

    source: MedicalSource = Relationship(back_populates="documents")
    chunks: list["DocumentChunk"] = Relationship(back_populates="document")


class DocumentChunk(SQLModel, table=True):
    __tablename__ = "document_chunks"

    id: str = Field(primary_key=True)
    document_id: int = Field(foreign_key="source_documents.id", index=True)
    chunk_type: str
    section_path: str
    page_number: int | None = None
    text_content: str
    embedding_id: str | None = None
    generic_name: str | None = Field(default=None, index=True)
    brand_names: str | None = None
    drug_entity_id: str | None = None
    source_trust_tier: int | None = None

    document: SourceDocument = Relationship(back_populates="chunks")
