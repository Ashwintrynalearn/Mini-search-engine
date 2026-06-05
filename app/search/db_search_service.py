import math
import time

from app.database import get_connection
from app.indexing.tokenizer import tokenize
from app.search.snippet import generate_snippet


def get_total_documents() -> int:
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) AS count FROM documents")
    total_documents = cursor.fetchone()["count"]

    connection.close()
    return total_documents


def search_documents(query: str, page: int = 1, size: int = 10) -> dict:
    """
    Searches SQLite postings using TF-IDF ranking.
    """
    start_time = time.perf_counter()

    query_terms = tokenize(query)
    total_documents = get_total_documents()

    if total_documents == 0 or not query_terms:
        return {
            "query": query,
            "page": page,
            "size": size,
            "totalResults": 0,
            "totalPages": 0,
            "latencyMs": 0,
            "results": [],
        }

    connection = get_connection()
    cursor = connection.cursor()

    scores: dict[int, float] = {}

    for term in query_terms:
        cursor.execute(
            """
            SELECT id FROM terms WHERE term = ?
            """,
            (term,),
        )

        term_row = cursor.fetchone()

        if term_row is None:
            continue

        term_id = term_row["id"]

        cursor.execute(
            """
            SELECT COUNT(*) AS document_frequency
            FROM postings
            WHERE term_id = ?
            """,
            (term_id,),
        )

        document_frequency = cursor.fetchone()["document_frequency"]

        if document_frequency == 0:
            continue

        idf = math.log(total_documents / document_frequency)

        cursor.execute(
            """
            SELECT document_id, frequency
            FROM postings
            WHERE term_id = ?
            """,
            (term_id,),
        )

        posting_rows = cursor.fetchall()

        for row in posting_rows:
            document_id = row["document_id"]
            frequency = row["frequency"]

            scores[document_id] = scores.get(document_id, 0.0) + frequency * idf

    ranked_document_ids = sorted(
        scores.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    total_results = len(ranked_document_ids)
    total_pages = math.ceil(total_results / size) if size > 0 else 0

    start_index = (page - 1) * size
    end_index = start_index + size
    paginated_results = ranked_document_ids[start_index:end_index]

    results = []

    for document_id, score in paginated_results:
        cursor.execute(
            """
            SELECT id, title, source, content
            FROM documents
            WHERE id = ?
            """,
            (document_id,),
        )

        document = cursor.fetchone()

        if document is None:
            continue

        snippet = generate_snippet(
            content=document["content"],
            query=query,
        )

        results.append(
            {
                "documentId": document["id"],
                "title": document["title"],
                "source": document["source"],
                "score": round(score, 4),
                "snippet": snippet,
            }
        )

    connection.close()

    latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

    return {
        "query": query,
        "page": page,
        "size": size,
        "totalResults": total_results,
        "totalPages": total_pages,
        "latencyMs": latency_ms,
        "results": results,
    }