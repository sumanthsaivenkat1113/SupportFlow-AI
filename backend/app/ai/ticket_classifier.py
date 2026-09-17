import json
import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is not set.")

client = Groq(api_key=GROQ_API_KEY)


CLASSIFIER_SYSTEM_PROMPT = """
You classify customer support tickets.

For each ticket choose exactly one:

- "automatable": A clear informational request that can be answered
  from general company policy or knowledge, without customer-specific
  investigation or action.

- "human_review": Anything requiring account, customer, order,
  payment investigation or action, fraud/security handling,
  legal/regulatory handling, exceptions, disputes, ambiguity,
  risk, or human judgment.

When uncertain, choose "human_review".

Confidence:
Return a number from 0 to 1.

Reason:
Return one short sentence with a maximum of 70 characters.
State only the main reason.
Do not explain your reasoning.
"""


CLASSIFIER_SCHEMA = {
    "type": "object",
    "properties": {
        "results": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "ticket_id": {"type": "integer"},
                    "classification": {
                        "type": "string",
                        "enum": ["automatable", "human_review"],
                    },
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                    "reason": {"type": "string", "maxLength": 100},
                },
                "required": ["ticket_id", "classification", "confidence", "reason"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["results"],
    "additionalProperties": False,
}


def classify_tickets(tickets: list[dict]) -> list[dict]:

    if not tickets:
        return []

    ticket_input = [
        {
            "ticket_id": index,
            "subject": ticket.get("subject") or "",
            "description": (ticket.get("description") or "").strip(),
        }
        for index, ticket in enumerate(tickets, start=1)
    ]

    for ticket in ticket_input:
        if not ticket["description"]:
            raise ValueError(f"Ticket {ticket['ticket_id']} has an empty description.")

    response = client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=[
            {"role": "system", "content": CLASSIFIER_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": json.dumps(
                    ticket_input, ensure_ascii=False, separators=(",", ":")
                ),
            },
        ],
        temperature=0,
        reasoning_effort="none",
        include_reasoning=False,
        max_completion_tokens=1200,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "ticket_classifications",
                "strict": True,
                "schema": CLASSIFIER_SCHEMA,
            },
        },
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError("Classifier returned an empty response.")

    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError("Classifier returned invalid JSON.") from exc

    results = data.get("results")

    if not isinstance(results, list):
        raise ValueError("Classifier response does not contain results.")

    expected_ids = set(range(1, len(tickets) + 1))
    returned_ids = set()

    validated_results = []

    for result in results:

        ticket_id = result.get("ticket_id")
        classification = result.get("classification")
        confidence = result.get("confidence")
        reason = result.get("reason")

        if ticket_id not in expected_ids:
            raise ValueError(f"Invalid ticket_id returned: {ticket_id}")

        if ticket_id in returned_ids:
            raise ValueError(f"Duplicate ticket_id returned: {ticket_id}")

        returned_ids.add(ticket_id)

        if classification not in {"automatable", "human_review"}:
            raise ValueError(f"Invalid classification for ticket {ticket_id}")

        if not isinstance(confidence, (int, float)):
            raise ValueError(f"Invalid confidence for ticket {ticket_id}")

        if not 0 <= confidence <= 1:
            raise ValueError(f"Confidence out of range for ticket {ticket_id}")

        if not isinstance(reason, str):
            raise ValueError(f"Invalid reason for ticket {ticket_id}")

        reason = reason.strip()[:70]

        validated_results.append(
            {
                "ticket_index": ticket_id,
                "classification": classification,
                "confidence": confidence,
                "reason": reason,
            }
        )

    missing_ids = expected_ids - returned_ids

    if missing_ids:
        raise ValueError(f"Missing ticket results: {sorted(missing_ids)}")

    validated_results.sort(key=lambda item: item["ticket_index"])

    return validated_results
