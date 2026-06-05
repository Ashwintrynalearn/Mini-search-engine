from fastapi import APIRouter

from app.indexing.persistent_indexer import rebuild_index


router = APIRouter()


@router.post("/index")
def index_documents() -> dict:
    stats = rebuild_index()

    return {
        "status": "success",
        **stats,
    }