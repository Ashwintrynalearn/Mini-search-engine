from app.database import get_connection
from fastapi import APIRouter


router = APIRouter()


@router.get("/stats")
def get_stats() -> dict:
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) AS count FROM documents")
    documents_indexed = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) AS count FROM terms")
    unique_terms = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) AS count FROM postings")
    postings_count = cursor.fetchone()["count"]

    cursor.execute(
        """
        SELECT value
        FROM index_metadata
        WHERE key = ?
        """,
        ("last_indexed_at",),
    )

    metadata_row = cursor.fetchone()
    last_indexed_at = metadata_row["value"] if metadata_row else None

    connection.close()

    return {
        "documentsIndexed": documents_indexed,
        "uniqueTerms": unique_terms,
        "postingsCount": postings_count,
        "lastIndexedAt": last_indexed_at,
    }