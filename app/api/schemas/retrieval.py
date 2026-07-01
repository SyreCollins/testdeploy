from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, examples=["What is the dosage of amoxicillin?"])
    limit: int = Field(default=10, ge=1, le=50)
    generic_name_filter: str | None = Field(default=None, examples=["amoxicillin"])
    chunk_type_filter: str | None = Field(default=None, examples=["dosage", "contraindication"])
    min_trust_tier: int | None = Field(default=None, ge=1, le=4, examples=[2])


class SearchResultItem(BaseModel):
    citation_id: str
    text_content: str
    score: float
    section_path: str | None = None
    page_number: int | None = None
    generic_name: str | None = None
    chunk_type: str | None = None
    source_name: str | None = None
    source_version: str | None = None
    source_trust_tier: int | None = None
    document_title: str | None = None


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResultItem]
    total: int
