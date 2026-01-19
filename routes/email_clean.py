def extract_clean_text(text: str) -> str:
    """
    Clean raw email TEXT.
    Removes newlines, double spaces, weird symbols.
    """
    if not isinstance(text, str):
        return ""

    cleaned = (
        text.replace("\n", " ")
            .replace("\r", " ")
            .replace("\t", " ")
    )

    return " ".join(cleaned.split())
