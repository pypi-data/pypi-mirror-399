from __future__ import annotations

from typing import Any, Dict, Optional, Tuple
from sellium._http import HTTPClient
from sellium.types import ResponseMeta


class GroupsService:
    def __init__(self, http: HTTPClient) -> None:
        self._http = http

    # GET /groups
    def list(
        self,
        *,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> Tuple[Dict[str, Any], ResponseMeta]:
        params: Dict[str, Any] = {}
        if page is not None:
            params["page"] = page
        if limit is not None:
            params["limit"] = limit
        if active is not None:
            params["active"] = active
        if search:
            params["search"] = search
        return self._http.request("GET", "/groups", params=params)

    # POST /groups
    def create(self, payload: Dict[str, Any]) -> Tuple[Dict[str, Any], ResponseMeta]:
        return self._http.request("POST", "/groups", json_body=payload)

    # GET /groups/{groupId}
    def get(self, group_id: str) -> Tuple[Dict[str, Any], ResponseMeta]:
        return self._http.request("GET", f"/groups/{group_id}")

    # PATCH /groups/{groupId}
    def update(self, group_id: str, payload: Dict[str, Any]) -> Tuple[Dict[str, Any], ResponseMeta]:
        return self._http.request("PATCH", f"/groups/{group_id}", json_body=payload)

    # DELETE /groups/{groupId}
    def delete(self, group_id: str) -> Tuple[Dict[str, Any], ResponseMeta]:
        return self._http.request("DELETE", f"/groups/{group_id}")
