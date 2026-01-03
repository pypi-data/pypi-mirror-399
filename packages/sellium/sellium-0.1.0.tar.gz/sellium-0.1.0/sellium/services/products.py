from __future__ import annotations

from typing import Any, Dict, Optional, Tuple
from sellium._http import HTTPClient
from sellium.types import ResponseMeta


class ProductsService:
    def __init__(self, http: HTTPClient) -> None:
        self._http = http

    # GET /products
    def list(
        self,
        *,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        active: Optional[bool] = None,
        group_id: Optional[str] = None,
    ) -> Tuple[Dict[str, Any], ResponseMeta]:
        params: Dict[str, Any] = {}
        if page is not None:
            params["page"] = page
        if limit is not None:
            params["limit"] = limit
        if active is not None:
            params["active"] = active
        if group_id:
            params["group_id"] = group_id
        return self._http.request("GET", "/products", params=params)

    # POST /products
    def create(self, payload: Dict[str, Any]) -> Tuple[Dict[str, Any], ResponseMeta]:
        return self._http.request("POST", "/products", json_body=payload)

    # GET /products/{productId}
    def get(self, product_id: str) -> Tuple[Dict[str, Any], ResponseMeta]:
        return self._http.request("GET", f"/products/{product_id}")

    # PATCH /products/{productId}
    def update(self, product_id: str, payload: Dict[str, Any]) -> Tuple[Dict[str, Any], ResponseMeta]:
        return self._http.request("PATCH", f"/products/{product_id}", json_body=payload)

    # DELETE /products/{productId}
    def delete(self, product_id: str) -> Tuple[Dict[str, Any], ResponseMeta]:
        return self._http.request("DELETE", f"/products/{product_id}")
