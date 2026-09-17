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

MAX_COMPLETION_TOKENS = 2500
MAX_REASON_LENGTH = 70


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

IMPORTANT RULES:

- When uncertain, choose "human_review".
- Preserve the exact ticket_id.
- Never modify ticket_id.
- Return exactly one result for EVERY input ticket.
- Do not skip any ticket.
- Do not merge tickets.
- Do not add tickets that were not provided.
- The number of output results MUST equal the number of input tickets.

Confidence:
- Return a number between 0 and 1.

Reason:
- Maximum 70 characters.
- One short sentence.
- State only the main reason.
- Do not provide detailed reasoning.
"""


# ============================================================
# CLASSIFY TICKETS
# ============================================================


def classify_tickets(tickets: list[dict]) -> list[dict]:
    """
    Classify all normalized tickets using a single Groq request.

    Expected input:

    [
        {
            "ticket_id": "uuid",
            "description": "Customer cannot log in."
        }
    ]

    Returns:

    [
        {
            "ticket_id": "uuid",
            "classification": "human_review",
            "confidence": 0.95,
            "reason": "Requires account investigation."
        }
    ]
    """

    # --------------------------------------------------------
    # Empty input
    # --------------------------------------------------------

    if not tickets:
        return []

    # --------------------------------------------------------
    # Prepare and validate input
    # --------------------------------------------------------

    ticket_input: list[dict] = []

    for index, ticket in enumerate(tickets, start=1):

        if not isinstance(ticket, dict):
            raise ValueError(f"Normalized ticket {index} is not a valid object.")

        ticket_id = ticket.get("ticket_id")
        description = ticket.get("description")

        # ----------------------------------------------------
        # Validate ticket ID
        # ----------------------------------------------------

        if not ticket_id:
            raise ValueError(f"Normalized ticket {index} is missing ticket_id.")

        ticket_id = str(ticket_id).strip()

        if not ticket_id:
            raise ValueError(f"Normalized ticket {index} has an empty ticket_id.")

        try:
            UUID(ticket_id)
        except (ValueError, AttributeError) as exc:
            raise ValueError(f"Invalid ticket UUID: {ticket_id}") from exc

        # ----------------------------------------------------
        # Validate description
        # ----------------------------------------------------

        if description is None:
            raise ValueError(f"Ticket {ticket_id} has an empty description.")

        description = str(description).strip()

        if not description:
            raise ValueError(f"Ticket {ticket_id} has an empty description.")

        # ----------------------------------------------------
        # Add normalized input
        # ----------------------------------------------------

        ticket_input.append(
            {
                "ticket_id": ticket_id,
                "description": description,
            }
        )

    # --------------------------------------------------------
    # Detect duplicate input IDs
    # --------------------------------------------------------

    input_ids = [ticket["ticket_id"] for ticket in ticket_input]

    if len(input_ids) != len(set(input_ids)):
        seen = set()
        duplicates = []

        for ticket_id in input_ids:
            if ticket_id in seen:
                duplicates.append(ticket_id)
            else:
                seen.add(ticket_id)

        raise ValueError(f"Duplicate ticket_id values found: {duplicates}")

    expected_count = len(ticket_input)

    # ========================================================
    # JSON SCHEMA
    # ========================================================

    classifier_schema = {
        "type": "object",
        "properties": {
            "results": {
                "type": "array",
                "minItems": expected_count,
                "maxItems": expected_count,
                "items": {
                    "type": "object",
                    "properties": {
                        "ticket_id": {"type": "string"},
                        "classification": {
                            "type": "string",
                            "enum": [
                                "automatable",
                                "human_review",
                            ],
                        },
                        "confidence": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 1,
                        },
                        "reason": {
                            "type": "string",
                            "maxLength": MAX_REASON_LENGTH,
                        },
                    },
                    "required": [
                        "ticket_id",
                        "classification",
                        "confidence",
                        "reason",
                    ],
                    "additionalProperties": False,
                },
            }
        },
        "required": ["results"],
        "additionalProperties": False,
    }

    # ========================================================
    # USER PROMPT
    # ========================================================

    user_prompt = (
        f"Classify exactly {expected_count} tickets.\n"
        f"Return exactly {expected_count} results.\n"
        f"Every ticket_id must appear exactly once.\n"
        f"Do not omit any ticket.\n\n"
        f"INPUT TICKETS:\n"
        f"{json.dumps(
            ticket_input,
            ensure_ascii=False,
            separators=(",", ":"),
        )}"
    )

    # ========================================================
    # GROQ REQUEST
    # ========================================================

    try:

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": CLASSIFIER_SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            temperature=0,
            max_completion_tokens=MAX_COMPLETION_TOKENS,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "ticket_classifications",
                    "strict": True,
                    "schema": classifier_schema,
                },
            },
        )

    except Exception as exc:
        raise RuntimeError(f"Groq classification request failed: {exc}") from exc

    # ========================================================
    # VALIDATE GROQ RESPONSE
    # ========================================================

    if not response.choices:
        raise ValueError("Groq returned no choices.")

    message = response.choices[0].message
    content = message.content

    if not content:
        raise ValueError("Groq returned an empty response.")

    # ========================================================
    # PARSE JSON
    # ========================================================

    try:
        data = json.loads(content)

    except json.JSONDecodeError as exc:
        raise ValueError(f"Groq returned invalid JSON: {content}") from exc

    if not isinstance(data, dict):
        raise ValueError("Groq response must be a JSON object.")

    results = data.get("results")

    if not isinstance(results, list):
        raise ValueError("Groq response does not contain a valid results array.")

    # ========================================================
    # VALIDATE RESULT COUNT
    # ========================================================

    if len(results) != expected_count:
        raise ValueError(
            f"AI returned {len(results)} results " f"for {expected_count} tickets."
        )

    # ========================================================
    # EXPECTED IDS
    # ========================================================

    expected_ids = {ticket["ticket_id"] for ticket in ticket_input}

    returned_ids: set[str] = set()
    validated_results: list[dict] = []

    # ========================================================
    # VALIDATE EACH RESULT
    # ========================================================

    for index, result in enumerate(results, start=1):

        if not isinstance(result, dict):
            raise ValueError(f"AI result {index} is not a valid object.")

        ticket_id = result.get("ticket_id")
        classification = result.get("classification")
        confidence = result.get("confidence")
        reason = result.get("reason")

        # ----------------------------------------------------
        # Ticket ID
        # ----------------------------------------------------

        if not isinstance(ticket_id, str):
            raise ValueError(f"AI result {index} has an invalid ticket_id.")

        ticket_id = ticket_id.strip()

        if ticket_id not in expected_ids:
            raise ValueError(f"Invalid ticket_id returned by AI: {ticket_id}")

        if ticket_id in returned_ids:
            raise ValueError(f"Duplicate ticket_id returned by AI: {ticket_id}")

        returned_ids.add(ticket_id)

        # ----------------------------------------------------
        # Classification
        # ----------------------------------------------------

        if classification not in {
            "automatable",
            "human_review",
        }:
            raise ValueError(
                f"Invalid classification for ticket " f"{ticket_id}: {classification}"
            )

        # ----------------------------------------------------
        # Confidence
        # ----------------------------------------------------

        if isinstance(confidence, bool) or not isinstance(
            confidence,
            (int, float),
        ):
            raise ValueError(f"Invalid confidence for ticket {ticket_id}")

        confidence = float(confidence)

        if not 0 <= confidence <= 1:
            raise ValueError(f"Confidence out of range for ticket {ticket_id}")

        # ----------------------------------------------------
        # Reason
        # ----------------------------------------------------

        if not isinstance(reason, str):
            raise ValueError(f"Invalid reason for ticket {ticket_id}")

        reason = reason.strip()

        if not reason:
            raise ValueError(f"Empty reason for ticket {ticket_id}")

        if len(reason) > MAX_REASON_LENGTH:
            reason = reason[:MAX_REASON_LENGTH].rstrip()

        # ----------------------------------------------------
        # Add validated result
        # ----------------------------------------------------

        validated_results.append(
            {
                "ticket_id": ticket_id,
                "classification": classification,
                "confidence": confidence,
                "reason": reason,
            }
        )

    # ========================================================
    # CHECK FOR MISSING IDS
    # ========================================================

    missing_ids = expected_ids - returned_ids

    if missing_ids:
        raise ValueError("AI did not classify these tickets: " f"{sorted(missing_ids)}")

    # ========================================================
    # KEEP ORIGINAL INPUT ORDER
    # ========================================================

    order = {ticket["ticket_id"]: index for index, ticket in enumerate(ticket_input)}

    validated_results.sort(key=lambda item: order[item["ticket_id"]])

    # ========================================================
    # FINAL COUNT CHECK
    # ========================================================

    if len(validated_results) != expected_count:
        raise ValueError(
            f"Classification count mismatch: "
            f"{len(validated_results)} != {expected_count}"
        )

    return validated_results
