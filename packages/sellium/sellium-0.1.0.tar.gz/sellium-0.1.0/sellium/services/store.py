from __future__ import annotations

from typing import Any, Dict, Tuple
from sellium._http import HTTPClient
from sellium.types import ResponseMeta


class StoreService:
    def __init__(self, http: HTTPClient) -> None:
        self._http = http

    # GET /store
    def get(self) -> Tuple[Dict[str, Any], ResponseMeta]:
        return self._http.request("GET", "/store")
