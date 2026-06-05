from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Union

from app.database import get_connection, initialize_database
from app.indexing.tokenizer import tokenize


BASE_DIR = Path(__file__).resolve().parent.parent.parent
DOCS_DIR = BASE_DIR / "data" / "docs"


def clear_index() -> None:
    """
    Clears all existing indexed data.
    """
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM postings")
    cursor.execute("DELETE FROM terms")
    cursor.execute("DELETE FROM documents")
    cursor.execute("DELETE FROM index_metadata")

    connection.commit()
    connection.close()


def load_local_documents() -> dict[str, str]:
    """
    Reads all .txt files from backend/data/docs.
    Returns document_name -> content.
    """
    if not DOCS_DIR.exists():
        raise FileNotFoundError(f"Docs directory not found: {DOCS_DIR}")

    documents = {}

    for file_path in DOCS_DIR.glob("*.txt"):
        documents[file_path.name] = file_path.read_text(encoding="utf-8")

    return documents


def save_metadata(key: str, value: str) -> None:
    """
    Saves metadata key-value pairs.
    """
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT OR REPLACE INTO index_metadata (key, value)
        VALUES (?, ?)
        """,
        (key, value),
    )

    connection.commit()
    connection.close()


def rebuild_index() -> dict[str, Union[int, str]]:
    """
    Rebuilds the full SQLite-backed index from local .txt documents.
    """
    initialize_database()
    clear_index()

    documents = load_local_documents()

    connection = get_connection()
    cursor = connection.cursor()

    postings_count = 0

    for document_name, content in documents.items():
        source = f"local://{document_name}"
        title = document_name

        cursor.execute(
            """
            INSERT INTO documents (title, source, content)
            VALUES (?, ?, ?)
            """,
            (title, source, content),
        )

        document_id = cursor.lastrowid

        tokens = tokenize(content)
        term_frequencies = Counter(tokens)

        for term, frequency in term_frequencies.items():
            cursor.execute(
                """
                INSERT OR IGNORE INTO terms (term)
                VALUES (?)
                """,
                (term,),
            )

            cursor.execute(
                """
                SELECT id FROM terms WHERE term = ?
                """,
                (term,),
            )

            term_id = cursor.fetchone()["id"]

            cursor.execute(
                """
                INSERT INTO postings (term_id, document_id, frequency)
                VALUES (?, ?, ?)
                """,
                (term_id, document_id, frequency),
            )

            postings_count += 1

    cursor.execute("SELECT COUNT(*) AS count FROM terms")
    unique_terms = cursor.fetchone()["count"]

    indexed_at = datetime.now(timezone.utc).isoformat()

    cursor.execute(
        """
        INSERT OR REPLACE INTO index_metadata (key, value)
        VALUES (?, ?)
        """,
        ("last_indexed_at", indexed_at),
    )

    connection.commit()
    connection.close()

    return {
        "documentsIndexed": len(documents),
        "uniqueTerms": unique_terms,
        "postingsCount": postings_count,
        "lastIndexedAt": indexed_at,
    }