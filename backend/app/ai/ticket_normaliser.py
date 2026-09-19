# app/ai/ticket_normaliser.py

import json
import os
from uuid import UUID

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is not set in the environment.")

client = Groq(api_key=GROQ_API_KEY)

MODEL_NAME = "qwen/qwen3.8-27b"

NORMALIZER_SYSTEM_PROMPT = """
You are a customer support ticket normalizer.

You will receive a JSON array. Each element has:
- "internal_id": a stable identifier you must echo back EXACTLY, unchanged.
- "raw_ticket": the ticket exactly as it arrived from some external
  system. Its shape is UNKNOWN and varies per ticket — it might be
  flat, deeply nested, or use completely different field names
  (examples across different sources: "ticket_id", "id", "key",
  "ticket.number"; "issues", "description", "details.body",
  "fields.description", "details.summary", "fields.summary", or
  something else entirely not listed here).

For each element, do the following:

1. Find the human-facing ticket identifier somewhere inside
   raw_ticket (it is usually a short code or number field near the
   top level or one level deep, e.g. "F1-1001", "CUST-3001",
   "F4-4002"). If you cannot confidently find one, use the
   internal_id string as the ticket_id instead.

2. Find the customer's issue / complaint / request text — this is
   usually the longest free-text field describing what the customer
   needs (subject + body/description combined if both exist, but
   prioritize the fuller description over just the subject line).
   Rewrite it into a clear, concise, third-person summary that
   preserves the customer's intent. Do not invent details that
   aren't present. Do not drop important specifics (order numbers,
   error conditions, etc).

Rules:
- Return EXACTLY ONE result per input element — never more, never
  fewer. Do not repeat any internal_id.
- Always echo internal_id back unchanged.
- ticket_id must never be empty (fall back to internal_id if unsure).
- Keep description under 200 characters.
- Output must be valid JSON matching the schema exactly.
"""

NORMALIZER_SCHEMA = {
    "type": "object",
    "properties": {
        "results": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "internal_id": {"type": "string"},
                    "ticket_id": {"type": "string"},
                    "description": {"type": "string"},
                },
                "required": ["internal_id", "ticket_id", "description"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["results"],
    "additionalProperties": False,
}


def _call_groq(ticket_input: list[dict]) -> list[dict]:
    """Single Groq call. Returns the raw 'results' list (unvalidated)."""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": NORMALIZER_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": json.dumps(
                    ticket_input,
                    ensure_ascii=False,
                    separators=(",", ":"),
                    default=str,
                ),
            },
        ],
        temperature=0,
        max_completion_tokens=1500,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "ticket_normalizations",
                "strict": True,
                "schema": NORMALIZER_SCHEMA,
            },
        },
    )

    if not response.choices:
        raise ValueError("Groq returned no choices.")

    content = response.choices[0].message.content
    if not content:
        raise ValueError("Groq returned an empty response.")

    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Groq returned invalid JSON: {content}") from exc

    results = data.get("results")
    if not isinstance(results, list):
        raise ValueError("Groq response does not contain a results array.")

    return results


def _validate_results(
    results: list[dict],
    expected_ids: set[str],
) -> dict[str, dict]:
    """
    Validate raw AI results against expected internal_ids.

    Tolerant of model noise: unknown internal_ids (hallucinated rows)
    and duplicate internal_ids (the model repeating a row) are simply
    ignored rather than treated as fatal — only the FIRST valid result
    per internal_id is kept. This is deliberately lenient because
    smaller/free-tier models can over-generate rows even with a
    strict schema and temperature=0; that noise is not a data
    integrity problem as long as every expected ticket ends up with
    exactly one usable result.

    Returns a dict of internal_id -> validated result. Does NOT raise
    on missing ids — the caller decides whether to retry or fail.
    """

    validated: dict[str, dict] = {}

    for result in results:
        internal_id = str(result.get("internal_id") or "")
        ticket_id = str(result.get("ticket_id") or "").strip()
        description = (result.get("description") or "").strip()

        # Ignore rows for tickets we never sent (hallucinated ids).
        if internal_id not in expected_ids:
            continue

        # Ignore repeats — keep the first valid occurrence only.
        if internal_id in validated:
            continue

        if not ticket_id:
            ticket_id = internal_id

        if not description:
            # A result with no usable description isn't valid;
            # skip it so a retry (or the missing-id check) can
            # catch it, rather than silently accepting empty text.
            continue

        validated[internal_id] = {
            "internal_id": internal_id,
            "ticket_id": ticket_id,
            "description": description,
        }

    return validated


def normalize_tickets(tickets: list[dict]) -> list[dict]:
    """
    Synchronous — call via asyncio.to_thread from the service.

    `tickets` is a list of {"internal_id": str, "raw_ticket": dict}.
    The raw_ticket shape is intentionally NOT constrained here —
    schema discovery (finding the id and description fields,
    however they're nested or named) is delegated to the model,
    since the number of possible source formats is unbounded.
    """

    if not tickets:
        return []

    ticket_input = []
    for ticket in tickets:
        internal_id = ticket.get("internal_id")
        raw_ticket = ticket.get("raw_ticket")

        if not internal_id:
            raise ValueError("Ticket is missing internal_id.")

        try:
            UUID(str(internal_id))
        except ValueError as exc:
            raise ValueError(f"internal_id is not a valid UUID: {internal_id}") from exc

        if not isinstance(raw_ticket, dict) or not raw_ticket:
            raise ValueError(f"Ticket {internal_id} has no raw_ticket data.")

        ticket_input.append({"internal_id": str(internal_id), "raw_ticket": raw_ticket})

    expected_ids = {t["internal_id"] for t in ticket_input}

    # ---------------------------------------------------------
    # First attempt.
    # ---------------------------------------------------------
    results = _call_groq(ticket_input)
    validated_by_id = _validate_results(results, expected_ids)

    missing = expected_ids - validated_by_id.keys()

    # ---------------------------------------------------------
    # If some tickets are still missing a valid result (e.g. the
    # model skipped one, or every candidate row for it had an
    # empty description), retry ONCE with just the missing subset
    # rather than failing the whole batch outright.
    # ---------------------------------------------------------
    if missing:
        retry_input = [t for t in ticket_input if t["internal_id"] in missing]
        retry_results = _call_groq(retry_input)
        retry_validated = _validate_results(retry_results, missing)
        validated_by_id.update(retry_validated)
        missing = expected_ids - validated_by_id.keys()

    if missing:
        raise ValueError(f"AI did not normalize these tickets: {sorted(missing)}")

    order = {t["internal_id"]: i for i, t in enumerate(ticket_input)}
    validated = sorted(
        validated_by_id.values(), key=lambda item: order[item["internal_id"]]
    )

    return validated
