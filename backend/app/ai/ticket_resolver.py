# ----------------------------------------------------------------------------------
# app/ai/ticket_resolver.py
# ----------------------------------------------------------------------------------

import asyncio
import json
import os
import time

from dotenv import load_dotenv
from groq import APIStatusError, AsyncGroq

# ----------------------------------------------------------------------------------
# Environment
# ----------------------------------------------------------------------------------

load_dotenv()

client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

MODEL_NAME = "openai/gpt-oss-120b"


# ----------------------------------------------------------------------------------
# Rate limiter (token bucket, TPM)
# ----------------------------------------------------------------------------------


class TPMRateLimiter:
    def __init__(self, tokens_per_minute: int):
        self.capacity = tokens_per_minute
        self.tokens = float(tokens_per_minute)
        self.refill_rate = tokens_per_minute / 60.0
        self.last_refill = time.monotonic()
        self._lock = asyncio.Lock()

    def _refill(self):
        now = time.monotonic()
        elapsed = now - self.last_refill

        self.tokens = min(
            self.capacity,
            self.tokens + elapsed * self.refill_rate,
        )

        self.last_refill = now

    async def acquire(self, amount: int) -> float:
        amount = min(amount, self.capacity)
        waited = 0.0

        async with self._lock:
            while True:
                self._refill()

                if self.tokens >= amount:
                    self.tokens -= amount
                    return waited

                needed = amount - self.tokens
                wait = needed / self.refill_rate

                waited += wait

                await asyncio.sleep(wait)

    async def sync_from_headers(self, remaining: int):
        async with self._lock:
            self.tokens = min(
                self.capacity,
                float(remaining),
            )

            self.last_refill = time.monotonic()


RATE_LIMITER = TPMRateLimiter(tokens_per_minute=7800)


# ----------------------------------------------------------------------------------
# Concurrency
# ----------------------------------------------------------------------------------

DEFAULT_CONCURRENCY = 5

_DEFAULT_SEM = asyncio.Semaphore(DEFAULT_CONCURRENCY)


# ----------------------------------------------------------------------------------
# System prompt
# ----------------------------------------------------------------------------------

SYSTEM_PROMPT = """
You are a customer support assistant.

Answer the customer's question using ONLY the provided context.

Rules:

1. Do not invent information.

2. If the answer is not in the context, set ticket_resolution to:
   "I couldn't find that information in the uploaded documents."

3. Keep the response concise and professional.

4. If the request requires human review, verification, escalation,
   account-specific action, security action, payment intervention,
   refund approval, or any action that cannot be safely completed
   automatically, set generated to "human-required".

5. If the customer's question can be answered completely using
   the provided context without human intervention, set generated
   to "ai-automated".

6. Do not promise a refund when the policy does not allow it.

7. Do not claim that an action was completed if the context only
   explains how the customer can perform the action.

8. generated MUST be exactly one of:
   - "ai-automated"
   - "human-required"

9. Always return both:
   - ticket_resolution
   - generated
"""


# ----------------------------------------------------------------------------------
# Structured JSON schema
# ----------------------------------------------------------------------------------

JSON_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "ticket_resolution",
        "schema": {
            "type": "object",
            "properties": {
                "ticket_resolution": {"type": "string"},
                "generated": {
                    "type": "string",
                    "enum": [
                        "ai-automated",
                        "human-required",
                    ],
                },
            },
            "required": [
                "ticket_resolution",
                "generated",
            ],
            "additionalProperties": False,
        },
    },
}


# ----------------------------------------------------------------------------------
# Token estimation
# ----------------------------------------------------------------------------------


def _estimate_tokens(text: str) -> int:
    """
    Rough token estimation.

    This is intentionally approximate and is only used
    for the local rate limiter.
    """
    return max(
        1,
        len(text) // 4,
    )


def _estimate_request_tokens(
    user_prompt: str,
    max_completion: int,
) -> int:
    return (
        _estimate_tokens(SYSTEM_PROMPT)
        + _estimate_tokens(user_prompt)
        + max_completion
        + 32
    )


# ----------------------------------------------------------------------------------
# Header helper
# ----------------------------------------------------------------------------------


def _parse_int_header(
    headers,
    name,
    default=None,
):
    value = headers.get(name)

    if value is None:
        return default

    try:
        return int(value)
    except (ValueError, TypeError):
        return default


# ----------------------------------------------------------------------------------
# Resolution generation
# ----------------------------------------------------------------------------------


async def generate_resolution(
    ticket_id: str,
    external_customer_id: str | None,
    question: str,
    context: str,
    max_completion: int = 250,
    max_retries: int = 3,
    semaphore: asyncio.Semaphore | None = None,
) -> dict:
    """
    Generate a grounded ticket resolution using Groq.

    The model returns:

    {
        "ticket_resolution": "...",
        "generated": "ai-automated" | "human-required"
    }

    `context` is the retrieved policy/knowledge text prepared
    by the service layer.

    `semaphore` allows the caller to control concurrency.
    """

    # --------------------------------------------------------------------------
    # Build user prompt
    # --------------------------------------------------------------------------

    user_prompt = f"Context:\n" f"{context}\n\n" f"Ticket:\n" f"{question}"

    estimated_tokens = _estimate_request_tokens(
        user_prompt=user_prompt,
        max_completion=max_completion,
    )

    ticket_start = time.perf_counter()

    limiter_wait_total = 0.0
    api_time_total = 0.0

    sem = semaphore or _DEFAULT_SEM

    # --------------------------------------------------------------------------
    # Concurrency control
    # --------------------------------------------------------------------------

    async with sem:

        for attempt in range(max_retries):

            # ------------------------------------------------------------------
            # Rate limiter
            # ------------------------------------------------------------------

            waited = await RATE_LIMITER.acquire(estimated_tokens)

            limiter_wait_total += waited

            api_start = time.perf_counter()

            try:

                # --------------------------------------------------------------
                # Groq request
                # --------------------------------------------------------------

                raw = await client.chat.completions.with_raw_response.create(
                    model=MODEL_NAME,
                    messages=[
                        {
                            "role": "system",
                            "content": SYSTEM_PROMPT,
                        },
                        {
                            "role": "user",
                            "content": user_prompt,
                        },
                    ],
                    temperature=0,
                    max_completion_tokens=max_completion,
                    reasoning_effort="low",
                    response_format=JSON_SCHEMA,
                )

                # --------------------------------------------------------------
                # Parse response
                # --------------------------------------------------------------

                completion = await raw.parse()

                api_time_total += time.perf_counter() - api_start

                # --------------------------------------------------------------
                # Sync rate limiter with Groq headers
                # --------------------------------------------------------------

                headers = raw.headers

                remaining_tokens = _parse_int_header(
                    headers,
                    "x-ratelimit-remaining-tokens",
                )

                if remaining_tokens is not None:
                    await RATE_LIMITER.sync_from_headers(remaining_tokens)

                # --------------------------------------------------------------
                # Extract model output
                # --------------------------------------------------------------

                content = completion.choices[0].message.content

                if not content:
                    raise ValueError(f"Empty model response for ticket {ticket_id}")

                llm_output = json.loads(content)

                # --------------------------------------------------------------
                # Validate generated value
                # --------------------------------------------------------------

                ticket_resolution = llm_output.get("ticket_resolution")

                generated = llm_output.get("generated")

                if not ticket_resolution:
                    raise ValueError(
                        f"Missing ticket_resolution for ticket {ticket_id}"
                    )

                if generated not in {
                    "ai-automated",
                    "human-required",
                }:
                    raise ValueError(
                        f"Invalid generated value for ticket "
                        f"{ticket_id}: {generated!r}"
                    )

                # --------------------------------------------------------------
                # Return normalized result
                # --------------------------------------------------------------

                return {
                    "ticket_id": ticket_id,
                    "external_customer_id": external_customer_id,
                    "ticket_resolution": ticket_resolution,
                    # IMPORTANT:
                    # This was missing in your previous implementation.
                    "generated": generated,
                    "context": context,
                    "model_name": MODEL_NAME,
                    "_timing": {
                        "total_seconds": round(
                            time.perf_counter() - ticket_start,
                            3,
                        ),
                        "limiter_wait_seconds": round(
                            limiter_wait_total,
                            3,
                        ),
                        "api_seconds": round(
                            api_time_total,
                            3,
                        ),
                    },
                }

            # ------------------------------------------------------------------
            # Rate-limit handling
            # ------------------------------------------------------------------

            except APIStatusError as e:

                api_time_total += time.perf_counter() - api_start

                if e.status_code == 429 and attempt < max_retries - 1:
                    retry_after = 5 * (2**attempt)

                    response = getattr(
                        e,
                        "response",
                        None,
                    )

                    if response is not None:

                        retry_after_header = response.headers.get("retry-after")

                        if retry_after_header:

                            try:
                                retry_after = float(retry_after_header)
                            except ValueError:
                                pass

                    await asyncio.sleep(retry_after)

                else:
                    raise

            # ------------------------------------------------------------------
            # JSON / validation errors
            # ------------------------------------------------------------------

            except (
                json.JSONDecodeError,
                KeyError,
                ValueError,
            ) as e:

                logger_message = f"Invalid LLM response for ticket " f"{ticket_id}: {e}"

                # Retry malformed model output if attempts remain.
                if attempt < max_retries - 1:
                    await asyncio.sleep(1 * (attempt + 1))
                    continue

                raise ValueError(logger_message) from e

    raise RuntimeError(f"{ticket_id} failed after {max_retries} retries")
