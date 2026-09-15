import json
from typing import Any


def json_to_json(file_bytes: bytes) -> list[dict[str, Any]]:
    """
    Parse a JSON file containing either:
      - a top-level list of ticket objects, or
      - a top-level object with a `tickets` array.

    Returns a list of ticket dicts.
    """
    try:
        data = json.loads(file_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Invalid JSON file") from exc

    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        # Common wrapper keys
        for key in ("tickets", "data", "records", "items"):
            if isinstance(data.get(key), list):
                return data[key]
        # A single ticket object
        return [data]

    raise ValueError("JSON file must contain an object or a list of objects")
