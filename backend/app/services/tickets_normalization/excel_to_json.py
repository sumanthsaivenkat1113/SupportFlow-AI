import io
from typing import Any

from openpyxl import load_workbook


def excel_to_json(file_bytes: bytes) -> list[dict[str, Any]]:
    """
    Convert the first sheet of an .xlsx/.xlsm file into a list of dicts.
    Row 1 is treated as the header.
    """
    try:
        wb = load_workbook(
            filename=io.BytesIO(file_bytes),
            read_only=True,
            data_only=True,
        )
    except Exception as exc:
        raise ValueError("Invalid Excel file") from exc

    sheet = wb.active
    rows = list(sheet.iter_rows(values_only=True))

    if not rows:
        raise ValueError("Excel file is empty")

    headers = [str(h).strip() if h is not None else "" for h in rows[0]]

    if not any(headers):
        raise ValueError("Excel file has no header row")

    tickets: list[dict[str, Any]] = []
    for row in rows[1:]:
        # Skip completely empty rows
        if all(cell is None for cell in row):
            continue
        ticket = {headers[i]: row[i] for i in range(len(headers)) if headers[i]}
        tickets.append(ticket)

    return tickets
