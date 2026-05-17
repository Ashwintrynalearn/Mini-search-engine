import re


def clean_text(text: str) -> str:
    """
    Converts text to lowercase, removes punctuation/special characters,
    and normalizes whitespace.
    """
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text