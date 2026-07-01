import logging

from fastapi import APIRouter, HTTPException, Request
from starlette import status

from app.api.schemas.admin import (
    IngestDocumentRequest,
    IngestDocumentResponse,
    RegisterSourceRequest,
    RegisterSourceResponse,
)
from app.rag.service import IngestionService

logger = logging.getLogger("zam-ai-core-api.admin-routes")
router = APIRouter()


@router.post(
    "/admin/sources",
    response_model=RegisterSourceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_source(
    request: Request, body: RegisterSourceRequest
) -> RegisterSourceResponse:
    svc: IngestionService = request.app.state.ingestion_service
    source = svc.register_source(
        name=body.name,
        publisher=body.publisher,
        version=body.version,
        license_status=body.license_status,
        jurisdiction=body.jurisdiction,
        trust_tier=body.trust_tier,
        publication_date=body.publication_date,
    )
    return RegisterSourceResponse(
        id=source.id,
        name=source.name,
        publisher=source.publisher,
        version=source.version,
        trust_tier=source.trust_tier,
        jurisdiction=source.jurisdiction,
    )


@router.post(
    "/admin/documents/ingest",
    response_model=IngestDocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def ingest_document(
    request: Request, body: IngestDocumentRequest
) -> IngestDocumentResponse:
    svc: IngestionService = request.app.state.ingestion_service
    source = svc.registry.get_source(body.source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source with id {body.source_id} not found",
        )
    try:
        result = svc.ingest_document(
            source=source,
            file_path=body.file_path,
            title=body.title,
            document_version=body.document_version,
        )
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e

    return IngestDocumentResponse(
        document_id=result["document_id"],
        status=result["status"],
        chunks_count=result["chunks_count"],
    )
