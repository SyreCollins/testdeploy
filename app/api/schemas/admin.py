from pydantic import BaseModel, Field


class RegisterSourceRequest(BaseModel):
    name: str = Field(examples=["NAFDAC Products"])
    publisher: str = Field(examples=["NAFDAC"])
    version: str = Field(examples=["2024-06"])
    license_status: str = Field(examples=["active"])
    jurisdiction: str = Field(examples=["NG"])
    trust_tier: int | None = Field(default=None, ge=1, le=4, examples=[3])
    publication_date: str | None = None


class RegisterSourceResponse(BaseModel):
    id: int
    name: str
    publisher: str
    version: str
    trust_tier: int | None
    jurisdiction: str


class IngestDocumentRequest(BaseModel):
    source_id: int = Field(examples=[1])
    file_path: str = Field(examples=["sources/nafdac_products DONE 2.csv"])
    title: str | None = None
    document_version: str | None = None


class IngestDocumentResponse(BaseModel):
    document_id: int
    status: str
    chunks_count: int
