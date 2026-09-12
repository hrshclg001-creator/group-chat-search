"""Search and corpus-statistics endpoints over the lifespan-owned service."""

from fastapi import APIRouter, Depends, HTTPException, Request

from ..schemas import SearchRequest, SearchResponse, StatsResponse
from ..services.search import SearchService, SearchUnavailable


router = APIRouter()


def get_search_service(request: Request):
    return request.app.state.search_service


@router.post('/search', response_model=SearchResponse)
def search(payload: SearchRequest, service: SearchService = Depends(get_search_service)):
    try:
        return service.search(payload.query, payload.top_k)
    except SearchUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get('/stats', response_model=StatsResponse)
def stats(service: SearchService = Depends(get_search_service)):
    return service.stats
