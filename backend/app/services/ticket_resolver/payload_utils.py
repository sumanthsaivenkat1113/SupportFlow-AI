# ----------------------------------------------------------------------------------
# app/services/ticket_resolver/payload_utils.py
# ----------------------------------------------------------------------------------
"""
Helpers for extracting data from raw Ticket JSON payloads.

The `Ticket` model may store its original payload as either a JSON/dict column or
as a JSON-encoded string. These helpers normalise that access so the rest of the
resolver code can assume a plain `dict`.
"""

import json
from typing import Any

# ------------------------------------------------------------------
# Attribute names on `Ticket` where a JSON payload might live.
# Ordered by likelihood — first match wins.
# ------------------------------------------------------------------
PAYLOAD_ATTRS: tuple[str, ...] = (
    "customer_ticket",
    "ticket_data",
    "ticket_payload",
    "payload",
    "data",
    "raw_data",
    "content",
    "ticket_json",
)

# ------------------------------------------------------------------
# Keys used to locate the external ticket number inside the payload.
# ------------------------------------------------------------------
TICKET_NUMBER_KEYS: tuple[str, ...] = (
    "ticket__number",
    "ticket_number",
    "ticket__id",
    "ticket_id",
    "external_id",
    "number",
)

# ------------------------------------------------------------------
# Keys used to locate the external customer id inside the payload.
# ------------------------------------------------------------------
CUSTOMER_ID_KEYS: tuple[str, ...] = (
    "customer__id",
    "customer_id",
    "external_customer_id",
)

# ------------------------------------------------------------------
# Keys used to locate the ticket body/description inside the payload.
# ------------------------------------------------------------------
BODY_KEYS: tuple[str, ...] = (
    "details__body",
    "body",
    "description",
    "summary",
)


def coerce_payload(raw: Any) -> dict | None:
    """
    Return a `dict` from a value that might be a dict, a JSON string, or bytes.

    Returns `None` if the value cannot be coerced into a dict.
    """
    if raw is None:
        return None

    if isinstance(raw, dict):
        return raw

    if isinstance(raw, (bytes, bytearray)):
        try:
            raw = raw.decode("utf-8")
        except Exception:
            return None

    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return None
        return parsed if isinstance(parsed, dict) else None

    return None


def first_key(payload: dict, keys: tuple[str, ...]) -> Any:
    """
    Return the first non-empty value found for any key in `keys`.

    A value is considered "empty" if it is `None` or an empty string.
    """
    for k in keys:
        v = payload.get(k)
        if v not in (None, ""):
            return v
    return None
