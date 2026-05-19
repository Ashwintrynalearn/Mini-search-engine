import math

from app.indexing.tokenizer import tokenize


def calculate_idf(
    term: str,
    inverted_index: dict[str, dict[str, int]],
    total_documents: int
) -> float:
    """
    Calculates inverse document frequency.

    IDF is higher for rare terms and lower for common terms.
    """
    document_frequency = len(inverted_index.get(term, {}))

    if document_frequency == 0:
        return 0.0

    return math.log(total_documents / document_frequency)


def search(
    query: str,
    inverted_index: dict[str, dict[str, int]],
    total_documents: int,
    limit: int = 10
) -> list[tuple[str, float]]:
    """
    Searches using TF-IDF scoring.

    score = term_frequency * inverse_document_frequency
    """
    query_terms = tokenize(query)
    scores: dict[str, float] = {}

    for term in query_terms:
        if term not in inverted_index:
            continue

        idf = calculate_idf(term, inverted_index, total_documents)

        for document_name, term_frequency in inverted_index[term].items():
            tf_idf_score = term_frequency * idf
            scores[document_name] = scores.get(document_name, 0.0) + tf_idf_score

    ranked_results = sorted(
        scores.items(),
        key=lambda item: item[1],
        reverse=True
    )

    return ranked_results[:limit]