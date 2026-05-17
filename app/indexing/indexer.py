from pathlib import Path
from collections import defaultdict, Counter

from app.indexing.tokenizer import tokenize


def load_documents(docs_dir: str) -> dict[str, str]:
    """
    Reads all .txt files from the docs directory.
    Returns a dictionary: document_name -> document_text.
    """
    documents = {}
    docs_path = Path(docs_dir)

    if not docs_path.exists():
        raise FileNotFoundError(f"Docs directory not found: {docs_dir}")

    for file_path in docs_path.glob("*.txt"):
        documents[file_path.name] = file_path.read_text(encoding="utf-8")

    return documents


def build_inverted_index(documents: dict[str, str]) -> dict[str, dict[str, int]]:
    """
    Builds an inverted index.

    Example:
    {
        "search": {
            "binary-search.txt": 3,
            "linear-search.txt": 2
        }
    }
    """
    inverted_index = defaultdict(dict)

    for document_name, content in documents.items():
        tokens = tokenize(content)
        term_frequencies = Counter(tokens)

        for term, frequency in term_frequencies.items():
            inverted_index[term][document_name] = frequency

    return dict(inverted_index)