import json
import os
from uuid import UUID

from dotenv import load_dotenv
from groq import Groq

# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is not set in the environment.")


client = Groq(api_key=GROQ_API_KEY)


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_NAME = "qwen/qwen3.8-27b"


# ============================================================
# SYSTEM PROMPT
# ============================================================

CLASSIFIER_SYSTEM_PROMPT = """
You are a customer support ticket classifier.

Classify every ticket into exactly one of these categories:

1. automatable
A clear informational request that can be answered using
general company policy or knowledge.

It must NOT require:
- customer-specific investigation
- account investigation
- payment investigation
- order investigation
- manual action
- human judgment

2. human_review
Anything that requires:
- customer-specific investigation
- account investigation
- order investigation
- payment investigation
- fraud/security handling
- legal/regulatory handling
- refund investigation
- exceptions
- disputes
- ambiguity
- risk
- human judgment
- manual action

IMPORTANT:
- When uncertain, choose "human_review".
- Preserve the exact ticket_id.
- Do not modify ticket_id.
- Return exactly one result for every input ticket.

Confidence:
Return a number between 0 and 1.

Reason:
- Maximum 70 characters.
- One short sentence.
- State only the main reason.
- Do not provide detailed reasoning.
"""


# ============================================================
# JSON SCHEMA
# ============================================================

CLASSIFIER_SCHEMA = {
    "type": "object",
    "properties": {
        "results": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "ticket_id": {"type": "string"},
                    "classification": {
                        "type": "string",
                        "enum": ["automatable", "human_review"],
                    },
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                    "reason": {"type": "string", "maxLength": 70},
                },
                "required": ["ticket_id", "classification", "confidence", "reason"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["results"],
    "additionalProperties": False,
}


# ============================================================
# CLASSIFY TICKETS
# ============================================================


def classify_tickets(
    tickets: list[dict],
) -> list[dict]:

    if not tickets:
        return []

    # --------------------------------------------------------
    # Prepare input
    # --------------------------------------------------------

    ticket_input = []

    for ticket in tickets:

        ticket_id = ticket.get("ticket_id")
        description = ticket.get("description")

        if not ticket_id:
            raise ValueError("Normalized ticket is missing ticket_id.")

        if not description:
            raise ValueError(f"Ticket {ticket_id} has an empty description.")

        # Validate UUID
        try:
            UUID(str(ticket_id))
        except ValueError as exc:
            raise ValueError(f"Invalid ticket UUID: {ticket_id}") from exc

        ticket_input.append(
            {
                "ticket_id": str(ticket_id),
                "description": description.strip(),
            }
        )

    # --------------------------------------------------------
    # Send ONE request to Groq
    # --------------------------------------------------------

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": CLASSIFIER_SYSTEM_PROMPT,
            },
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
        max_completion_tokens=900,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "ticket_classifications",
                "strict": True,
                "schema": CLASSIFIER_SCHEMA,
            },
        },
    )

    # --------------------------------------------------------
    # Get response content
    # --------------------------------------------------------

    if not response.choices:
        raise ValueError("Groq returned no choices.")

    content = response.choices[0].message.content

    if not content:
        raise ValueError("Groq returned an empty response.")

    # --------------------------------------------------------
    # Parse JSON
    # --------------------------------------------------------

    try:
        data = json.loads(content)

    except json.JSONDecodeError as exc:
        raise ValueError(f"Groq returned invalid JSON: {content}") from exc

    results = data.get("results")

    if not isinstance(results, list):
        raise ValueError("Groq response does not contain a valid results array.")

    # --------------------------------------------------------
    # Validate returned IDs
    # --------------------------------------------------------

    expected_ids = {str(ticket["ticket_id"]) for ticket in ticket_input}

    returned_ids = set()

    validated_results = []

    for result in results:

        ticket_id = result.get("ticket_id")
        classification = result.get("classification")
        confidence = result.get("confidence")
        reason = result.get("reason")

        # ----------------------------------------------------
        # Validate ticket ID
        # ----------------------------------------------------

        if ticket_id not in expected_ids:
            raise ValueError(f"Invalid ticket_id returned by AI: {ticket_id}")

        if ticket_id in returned_ids:
            raise ValueError(f"Duplicate ticket_id returned by AI: {ticket_id}")

        returned_ids.add(ticket_id)

        # ----------------------------------------------------
        # Validate classification
        # ----------------------------------------------------

        if classification not in {
            "automatable",
            "human_review",
        }:
            raise ValueError(
                f"Invalid classification for ticket {ticket_id}: " f"{classification}"
            )

        # ----------------------------------------------------
        # Validate confidence
        # ----------------------------------------------------

        if not isinstance(
            confidence,
            (int, float),
        ):
            raise ValueError(f"Invalid confidence for ticket {ticket_id}")

        if not 0 <= confidence <= 1:
            raise ValueError(f"Confidence out of range for ticket {ticket_id}")

        # ----------------------------------------------------
        # Validate reason
        # ----------------------------------------------------

        if not isinstance(reason, str):
            raise ValueError(f"Invalid reason for ticket {ticket_id}")

        reason = reason.strip()

        if len(reason) > 70:
            reason = reason[:70].rstrip()

        validated_results.append(
            {
                "ticket_id": str(ticket_id),
                "classification": classification,
                "confidence": float(confidence),
                "reason": reason,
            }
        )

    # --------------------------------------------------------
    # Check missing tickets
    # --------------------------------------------------------

    missing_ids = expected_ids - returned_ids

    if missing_ids:
        raise ValueError(
            f"AI did not classify these tickets: " f"{sorted(missing_ids)}"
        )

    # --------------------------------------------------------
    # Keep original ticket order
    # --------------------------------------------------------

    order = {
        str(ticket["ticket_id"]): index for index, ticket in enumerate(ticket_input)
    }

    validated_results.sort(key=lambda item: order[item["ticket_id"]])

    return validated_results
