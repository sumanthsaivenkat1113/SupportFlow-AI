# ----------------------------------------------------------------------------------
# app/services/ticket_resolver/__init__.py
# ----------------------------------------------------------------------------------
"""
Ticket resolution service.

Public API:
    - resolve_workspace_tickets   : run the full pipeline (write path)
    - list_workspace_ticket_resolutions : list persisted rows (read path)
"""

from app.services.ticket_resolver.listing import list_workspace_ticket_resolutions
from app.services.ticket_resolver.orchestrator import resolve_workspace_tickets

__all__ = [
    "resolve_workspace_tickets",
    "list_workspace_ticket_resolutions",
]
