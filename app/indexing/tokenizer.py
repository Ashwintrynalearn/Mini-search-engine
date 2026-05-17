from app.indexing.cleaner import clean_text


STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "were",
    "in", "on", "of", "to", "for", "by", "and",
    "or", "from", "with", "as", "at", "this", "that"
}


def tokenize(text: str) -> list[str]:
    """
    Cleans text, splits it into tokens, and removes common stop words.
    """
    cleaned_text = clean_text(text)
    tokens = cleaned_text.split()
    return [token for token in tokens if token not in STOP_WORDS]