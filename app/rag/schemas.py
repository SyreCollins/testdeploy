from sqlmodel import SQLModel


class Citation(SQLModel):
    citation_id: str
    source_name: str
    source_version: str
    source_trust_tier: int | None = None
    document_title: str
    section_path: str
    page_number: int | None = None
    text_content: str
