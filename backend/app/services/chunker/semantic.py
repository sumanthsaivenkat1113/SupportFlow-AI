import math
import re


def split_sentences(text: str) -> list[str]:
    sentences = re.split(
        r"(?<=[.!?])\s+",
        text.strip(),
    )

    return [sentence.strip() for sentence in sentences if sentence.strip()]


def cosine_similarity(
    a: list[float],
    b: list[float],
) -> float:

    if len(a) != len(b):
        raise ValueError("Embedding dimensions must match")

    dot_product = sum(x * y for x, y in zip(a, b))

    magnitude_a = math.sqrt(sum(x * x for x in a))

    magnitude_b = math.sqrt(sum(x * x for x in b))

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)


def find_breakpoints(
    embeddings: list[list[float]],
    percentile: float = 15,
) -> list[int]:

    similarities: list[float] = []

    for i in range(len(embeddings) - 1):

        similarity = cosine_similarity(
            embeddings[i],
            embeddings[i + 1],
        )

        similarities.append(similarity)

    if not similarities:
        return []

    sorted_values = sorted(similarities)

    index = int(len(sorted_values) * percentile / 100)

    index = min(
        index,
        len(sorted_values) - 1,
    )

    threshold = sorted_values[index]

    breakpoints: list[int] = []

    for i, similarity in enumerate(similarities):

        if similarity < threshold:
            breakpoints.append(i)

    return breakpoints


def create_chunks(
    sentences: list[str],
    embeddings: list[list[float]],
    percentile: float = 15,
) -> list[str]:

    if not sentences:
        return []

    if len(sentences) != len(embeddings):
        raise ValueError("Sentences and embeddings must have the same length")

    breakpoints = find_breakpoints(
        embeddings,
        percentile,
    )

    chunks: list[str] = []
    current: list[str] = []

    for i, sentence in enumerate(sentences):

        current.append(sentence)

        if i in breakpoints:

            chunks.append(" ".join(current).strip())

            current = []

    if current:
        chunks.append(" ".join(current).strip())

    return chunks
