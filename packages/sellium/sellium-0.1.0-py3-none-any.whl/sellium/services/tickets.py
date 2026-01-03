from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from sellium._http import HTTPClient
from sellium.types import ResponseMeta


class TicketsService:
    def __init__(self, http: HTTPClient) -> None:
        self._http = http

    # GET /tickets
    def list(
        self,
        *,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        email: Optional[str] = None,
    ) -> Tuple[Dict[str, Any], ResponseMeta]:
        params: Dict[str, Any] = {}
        if page is not None:
            params["page"] = page
        if limit is not None:
            params["limit"] = limit
        if status:
            params["status"] = status
        if priority:
            params["priority"] = priority
        if email:
            params["email"] = email
        return self._http.request("GET", "/tickets", params=params)

    # GET /tickets/{ticketId}
    def get(self, ticket_id: str) -> Tuple[Dict[str, Any], ResponseMeta]:
        return self._http.request("GET", f"/tickets/{ticket_id}")

    # POST /tickets/{ticketId}/reply
    def reply(self, ticket_id: str, payload: Dict[str, Any]) -> Tuple[Dict[str, Any], ResponseMeta]:
        return self._http.request("POST", f"/tickets/{ticket_id}/reply", json_body=payload)

    # PATCH /tickets/{ticketId}
    def update(self, ticket_id: str, payload: Dict[str, Any]) -> Tuple[Dict[str, Any], ResponseMeta]:
        return self._http.request("PATCH", f"/tickets/{ticket_id}", json_body=payload)
