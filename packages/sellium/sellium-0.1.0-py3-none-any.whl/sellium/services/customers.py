from __future__ import annotations

from typing import Any, Dict, Optional, Tuple
from urllib.parse import quote
from sellium._http import HTTPClient
from sellium.types import ResponseMeta


class CustomersService:
    def __init__(self, http: HTTPClient) -> None:
        self._http = http

    # GET /customers
    def list(
        self,
        *,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        email: Optional[str] = None,
    ) -> Tuple[Dict[str, Any], ResponseMeta]:
        params: Dict[str, Any] = {}
        if page is not None:
            params["page"] = page
        if limit is not None:
            params["limit"] = limit
        if email:
            params["email"] = email
        return self._http.request("GET", "/customers", params=params)

    # GET /customers/{email}
    def get(self, email: str) -> Tuple[Dict[str, Any], ResponseMeta]:
        return self._http.request("GET", f"/customers/{quote(email, safe='')}")
