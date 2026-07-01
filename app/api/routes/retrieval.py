import logging

from fastapi import APIRouter, HTTPException, Request
from starlette import status

from app.api.schemas.retrieval import SearchRequest, SearchResponse, SearchResultItem
from app.rag.service import RetrievalService

logger = logging.getLogger("zam-ai-core-api.retrieval-routes")
router = APIRouter()


@router.post("/retrieval/search", response_model=SearchResponse)
async def search(request: Request, body: SearchRequest) -> SearchResponse:
    svc: RetrievalService = request.app.state.retrieval_service
    try:
        results = svc.search(
            query=body.query,
            limit=body.limit,
            generic_name_filter=body.generic_name_filter,
            chunk_type_filter=body.chunk_type_filter,
            min_trust_tier=body.min_trust_tier,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e

    return SearchResponse(
        query=body.query,
        results=[SearchResultItem(**r) for r in results],
        total=len(results),
    )
