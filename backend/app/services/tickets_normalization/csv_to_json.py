import csv
import io
from typing import Any


def csv_to_json(file_bytes: bytes) -> list[dict[str, Any]]:
    """
    Convert CSV bytes into a list of dicts (header row required).
    Handles UTF-8 BOM and mixed line endings.
    """
    try:
        text = file_bytes.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("CSV file must be UTF-8 encoded") from exc

    reader = csv.DictReader(io.StringIO(text))

    if not reader.fieldnames:
        raise ValueError("CSV file has no header row")

    tickets: list[dict[str, Any]] = []
    for row in reader:
        # Skip blank lines
        if not any((v or "").strip() for v in row.values()):
            continue
        tickets.append({k: v for k, v in row.items() if k})

    return tickets
