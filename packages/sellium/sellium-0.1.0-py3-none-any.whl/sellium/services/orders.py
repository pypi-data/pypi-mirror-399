from __future__ import annotations

from typing import Any, Dict, Optional, Tuple
from sellium._http import HTTPClient
from sellium.types import ResponseMeta


class OrdersService:
    def __init__(self, http: HTTPClient) -> None:
        self._http = http

    # GET /orders
    def list(
        self,
        *,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        status: Optional[str] = None,
        product_id: Optional[str] = None,
        customer_email: Optional[str] = None,
    ) -> Tuple[Dict[str, Any], ResponseMeta]:
        params: Dict[str, Any] = {}
        if page is not None:
            params["page"] = page
        if limit is not None:
            params["limit"] = limit
        if status:
            params["status"] = status
        if product_id:
            params["product_id"] = product_id
        if customer_email:
            params["customer_email"] = customer_email
        return self._http.request("GET", "/orders", params=params)

    # POST /orders
    def create(self, payload: Dict[str, Any]) -> Tuple[Dict[str, Any], ResponseMeta]:
        return self._http.request("POST", "/orders", json_body=payload)

    # GET /orders/{orderId}
    def get(self, order_id: str) -> Tuple[Dict[str, Any], ResponseMeta]:
        return self._http.request("GET", f"/orders/{order_id}")

    # PATCH /orders/{orderId}
    def update(self, order_id: str, payload: Dict[str, Any]) -> Tuple[Dict[str, Any], ResponseMeta]:
        return self._http.request("PATCH", f"/orders/{order_id}", json_body=payload)
