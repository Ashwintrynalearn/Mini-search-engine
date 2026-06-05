from fastapi import APIRouter, Query

from app.search.db_search_service import search_documents


router = APIRouter()


@router.get("/search")
def search(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
) -> dict:
    return search_documents(query=q, page=page, size=size)