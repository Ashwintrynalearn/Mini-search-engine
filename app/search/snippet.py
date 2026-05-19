from app.indexing.cleaner import clean_text
from app.indexing.tokenizer import tokenize


def generate_snippet(
    content: str,
    query: str,
    window_size: int = 8
) -> str:
    """
    Generates a simple snippet around the first matched query term.

    window_size means number of words before and after the match.
    """
    cleaned_content = clean_text(content)
    words = cleaned_content.split()
    query_terms = set(tokenize(query))

    if not query_terms:
        return " ".join(words[: window_size * 2])

    match_index = None

    for index, word in enumerate(words):
        if word in query_terms:
            match_index = index
            break

    if match_index is None:
        return " ".join(words[: window_size * 2])

    start = max(match_index - window_size, 0)
    end = min(match_index + window_size + 1, len(words))

    snippet_words = words[start:end]
    snippet = " ".join(snippet_words)

    if start > 0:
        snippet = "... " + snippet

    if end < len(words):
        snippet = snippet + " ..."

    return snippet