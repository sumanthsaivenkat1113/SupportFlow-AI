import re

DEFAULT_CHUNK_SIZE = 500
DEFAULT_OVERLAP = 50


def estimate_tokens(text: str) -> int:
    """
    Simple token approximation.

    This is intentionally approximate because the exact
    Gemini tokenizer is not being used here.
    """

    return len(
        re.findall(
            r"\S+",
            text,
        )
    )


def create_chunks(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_OVERLAP,
) -> list[str]:

    words = text.split()

    if not words:
        return []

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks: list[str] = []

    start = 0

    while start < len(words):

        end = min(
            start + chunk_size,
            len(words),
        )

        chunk = " ".join(words[start:end]).strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(words):
            break

        start = end - overlap

    return chunks
