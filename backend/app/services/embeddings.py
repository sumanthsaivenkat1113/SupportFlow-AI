import asyncio
import os
import random
from app.core.config import settings
from google import genai
from google.genai import types

MODEL = "gemini-embedding-2"

DIMENSION = 768

MAX_CONCURRENT_REQUESTS = 5

MAX_RETRIES = 4


client = genai.Client(api_key=settings.GEMINI_API_KEY)


def _embed_text(
    text: str,
) -> list[float]:

    result = client.models.embed_content(
        model=MODEL,
        contents=text,
        config=types.EmbedContentConfig(
            output_dimensionality=DIMENSION,
        ),
    )

    return result.embeddings[0].values


async def _embed_with_retry(
    text: str,
    semaphore: asyncio.Semaphore,
) -> list[float]:

    async with semaphore:

        for attempt in range(MAX_RETRIES):

            try:

                return await asyncio.to_thread(
                    _embed_text,
                    text,
                )

            except Exception as error:

                error_message = str(error)

                if "429" not in error_message:
                    raise

                if attempt == MAX_RETRIES - 1:
                    raise

                wait_time = 2**attempt + random.uniform(0, 0.5)

                await asyncio.sleep(wait_time)

    raise RuntimeError("Failed to generate embedding")


async def embed_texts(
    texts: list[str],
) -> list[list[float]]:

    if not texts:
        return []

    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

    tasks = [
        _embed_with_retry(
            text,
            semaphore,
        )
        for text in texts
    ]

    return await asyncio.gather(*tasks)


def embed_text(
    text: str,
) -> list[float]:

    return _embed_text(text)
