import re

HEADING_PATTERN = re.compile(
    r"""
    ^
    (
        \d+(?:\.\d+)*[\s.)]+.+ |
        [A-Z][A-Z\s]{3,}$ |
        (?:Chapter|Section|Part)\s+\d+.*$
    )
    """,
    re.VERBOSE,
)


def is_heading(line: str) -> bool:
    line = line.strip()

    if not line:
        return False

    return bool(HEADING_PATTERN.match(line))


def create_chunks(text: str) -> list[str]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    if not lines:
        return []

    chunks: list[str] = []
    current: list[str] = []

    for line in lines:

        if is_heading(line) and current:
            chunks.append("\n".join(current).strip())
            current = []

        current.append(line)

    if current:
        chunks.append("\n".join(current).strip())

    return [chunk for chunk in chunks if chunk]
