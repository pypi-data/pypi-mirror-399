from __future__ import annotations

from typing import Any, Dict, Optional, Tuple
from sellium._http import HTTPClient
from sellium.types import ResponseMeta


class BlacklistService:
    def __init__(self, http: HTTPClient) -> None:
        self._http = http

    # GET /blacklist
    def list(
        self,
        *,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        type: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Tuple[Dict[str, Any], ResponseMeta]:
        params: Dict[str, Any] = {}
        if page is not None:
            params["page"] = page
        if limit is not None:
            params["limit"] = limit
        if type:
            params["type"] = type
        if search:
            params["search"] = search
        return self._http.request("GET", "/blacklist", params=params)

    # GET /blacklist/{entryId}
    def get(self, entry_id: str) -> Tuple[Dict[str, Any], ResponseMeta]:
        return self._http.request("GET", f"/blacklist/{entry_id}")

    # POST /blacklist
    def create(self, payload: Dict[str, Any]) -> Tuple[Dict[str, Any], ResponseMeta]:
        return self._http.request("POST", "/blacklist", json_body=payload)

    # DELETE /blacklist/{entryId}
    def delete(self, entry_id: str) -> Tuple[Dict[str, Any], ResponseMeta]:
        return self._http.request("DELETE", f"/blacklist/{entry_id}")
