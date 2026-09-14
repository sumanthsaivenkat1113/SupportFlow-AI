from app.services.chunker.semantic import (
    create_chunks as create_semantic_chunks,
    split_sentences,
)
from app.services.chunker.structure_aware import (
    create_chunks as create_structure_chunks,
)
from app.services.chunker.token_based import (
    create_chunks as create_token_chunks,
)


async def create_document_chunks(
    text: str,
    strategy: str,
) -> list[str]:

    if strategy == "Structure_aware":

        return create_structure_chunks(text)

    if strategy == "token_based_500":

        return create_token_chunks(
            text,
            chunk_size=500,
            overlap=50,
        )

    if strategy == "Semantic":

        # Semantic chunking requires temporary
        # sentence embeddings.

        from app.services.embeddings import embed_texts

        sentences = split_sentences(text)

        if not sentences:
            return []

        sentence_embeddings = await embed_texts(sentences)

        return create_semantic_chunks(
            sentences,
            sentence_embeddings,
        )

    raise ValueError(f"Unsupported chunking strategy: {strategy}")
