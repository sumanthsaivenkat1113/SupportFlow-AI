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

For each input ticket, rewrite the description into a clear,
concise, third-person summary that preserves the customer's
intent. Do not add information. Do not remove important detail.

Rules:
- Preserve the exact ticket_id. Do not modify it.
- Return exactly one result per input ticket.
- Keep the description under 200 characters.
- Output must be valid JSON matching the schema.
"""

NORMALIZER_SCHEMA = {
    "type": "object",
    "properties": {
        "results": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "ticket_id": {"type": "string"},
                    "description": {"type": "string"},
                },
                "required": ["ticket_id", "description"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["results"],
    "additionalProperties": False,
}


def normalize_tickets(tickets: list[dict]) -> list[dict]:
    """Synchronous — call via asyncio.to_thread from the service."""

    if not tickets:
        return []

    ticket_input = []
    for ticket in tickets:
        ticket_id = ticket.get("ticket_id")
        description = (ticket.get("description") or "").strip()

        if not ticket_id:
            raise ValueError("Ticket is missing ticket_id.")

        if not description:
            raise ValueError(f"Ticket {ticket_id} has an empty description.")

        try:
            UUID(str(ticket_id))
        except ValueError as exc:
            raise ValueError(f"Invalid ticket UUID: {ticket_id}") from exc

        ticket_input.append({"ticket_id": str(ticket_id), "description": description})

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

    expected_ids = {str(t["ticket_id"]) for t in ticket_input}
    returned_ids: set[str] = set()
    validated: list[dict] = []

    for result in results:
        ticket_id = str(result.get("ticket_id") or "")
        description = (result.get("description") or "").strip()

        if ticket_id not in expected_ids:
            raise ValueError(f"Invalid ticket_id returned by AI: {ticket_id}")

        if ticket_id in returned_ids:
            raise ValueError(f"Duplicate ticket_id returned by AI: {ticket_id}")

        returned_ids.add(ticket_id)

        if not description:
            raise ValueError(
                f"AI returned an empty description for ticket {ticket_id}."
            )

        validated.append({"ticket_id": ticket_id, "description": description})

    missing = expected_ids - returned_ids
    if missing:
        raise ValueError(f"AI did not normalize these tickets: {sorted(missing)}")

    order = {str(t["ticket_id"]): i for i, t in enumerate(ticket_input)}
    validated.sort(key=lambda item: order[item["ticket_id"]])

    return validated
