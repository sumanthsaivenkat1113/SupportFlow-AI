import asyncio
import json
import os
import time

from dotenv import load_dotenv
from groq import AsyncGroq, APIStatusError

load_dotenv()

client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

MODEL_NAME = "openai/gpt-oss-120b"


# ---------- Rate limiter (token bucket, TPM) ----------
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
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
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
            self.tokens = min(self.capacity, float(remaining))
            self.last_refill = time.monotonic()


RATE_LIMITER = TPMRateLimiter(tokens_per_minute=7800)

# 5 concurrent calls per batch (matches batch size)
CONCURRENCY = 5
SEM = asyncio.Semaphore(CONCURRENCY)


SYSTEM_PROMPT = """You are a customer support assistant.
Answer the customer's question using ONLY the provided context.
Rules:
1. Do not invent information.
2. If the answer is not in the context, set ticket_resolution to:
   "I couldn't find that information in the uploaded documents."
3. Keep it concise and professional.
4. If the policy requires human review, state that the ticket must be routed to a human support specialist.
5. Do not promise a refund when the policy does not allow it."""

JSON_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "ticket_resolution",
        "schema": {
            "type": "object",
            "properties": {"ticket_resolution": {"type": "string"}},
            "required": ["ticket_resolution"],
            "additionalProperties": False,
        },
    },
}


def _estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def _estimate_request_tokens(user_prompt: str, max_completion: int) -> int:
    return (
        _estimate_tokens(SYSTEM_PROMPT)
        + _estimate_tokens(user_prompt)
        + max_completion
        + 32
    )


def _parse_int_header(headers, name, default=None):
    v = headers.get(name)
    if v is None:
        return default
    try:
        return int(v)
    except (ValueError, TypeError):
        return default


async def generate_resolution(
    ticket_id: str,
    external_customer_id: str | None,
    question: str,
    context: str,
    max_completion: int = 250,
    max_retries: int = 3,
) -> dict:
    """
    Generate a grounded ticket resolution using Groq.
    `context` is the retrieved policy text (already prepared by the service layer).
    """
    # Minimal, token-efficient prompt
    user_prompt = f"Context:\n{context}\n\nTicket:\n{question}"

    est_tokens = _estimate_request_tokens(user_prompt, max_completion)
    ticket_start = time.perf_counter()
    limiter_wait_total = 0.0
    api_time_total = 0.0

    async with SEM:
        for attempt in range(max_retries):
            waited = await RATE_LIMITER.acquire(est_tokens)
            limiter_wait_total += waited

            api_start = time.perf_counter()
            try:
                raw = await client.chat.completions.with_raw_response.create(
                    model=MODEL_NAME,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0,
                    max_completion_tokens=max_completion,
                    reasoning_effort="low",
                    response_format=JSON_SCHEMA,
                )

                completion = await raw.parse()
                api_time_total += time.perf_counter() - api_start

                headers = raw.headers
                rl_remaining = _parse_int_header(
                    headers, "x-ratelimit-remaining-tokens"
                )
                if rl_remaining is not None:
                    await RATE_LIMITER.sync_from_headers(rl_remaining)

                llm_output = json.loads(completion.choices[0].message.content)

                return {
                    "ticket_id": ticket_id,
                    "external_customer_id": external_customer_id,
                    "ticket_resolution": llm_output["ticket_resolution"],
                    "context": context,
                    "model_name": MODEL_NAME,
                    "_timing": {
                        "total_seconds": round(time.perf_counter() - ticket_start, 3),
                        "limiter_wait_seconds": round(limiter_wait_total, 3),
                        "api_seconds": round(api_time_total, 3),
                    },
                }

            except APIStatusError as e:
                api_time_total += time.perf_counter() - api_start
                if e.status_code == 429 and attempt < max_retries - 1:
                    retry_after = 5 * (2**attempt)
                    hdrs = getattr(e, "response", None)
                    if hdrs is not None:
                        ra = hdrs.headers.get("retry-after")
                        if ra:
                            try:
                                retry_after = float(ra)
                            except ValueError:
                                pass
                    await asyncio.sleep(retry_after)
                else:
                    raise

    raise RuntimeError(f"{ticket_id} failed after {max_retries} retries")
