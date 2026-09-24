from typing import Literal

from pydantic import BaseModel


class TicketExportRequest(BaseModel):
    format: Literal["json", "csv", "excel"]
