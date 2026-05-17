from app.indexing.tokenizer import tokenize


def search(
    query: str,
    inverted_index: dict[str, dict[str, int]],
    limit: int = 10
) -> list[tuple[str, int]]:
    """
    Searches the inverted index and ranks documents by total matched term frequency.

    Returns:
    [
        ("binary-search.txt", 5),
        ("java-memory.txt", 2)
    ]
    """
    query_terms = tokenize(query)
    scores: dict[str, int] = {}

    for term in query_terms:
        if term not in inverted_index:
            continue

        for document_name, frequency in inverted_index[term].items():
            scores[document_name] = scores.get(document_name, 0) + frequency

    ranked_results = sorted(
        scores.items(),
        key=lambda item: item[1],
        reverse=True
    )

    return ranked_results[:limit]