from __future__ import annotations

from typing import Any, Dict, Optional, Tuple
from sellium._http import HTTPClient
from sellium.types import ResponseMeta


class CouponsService:
    def __init__(self, http: HTTPClient) -> None:
        self._http = http

    # GET /coupons
    def list(
        self,
        *,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        active: Optional[bool] = None,
        code: Optional[str] = None,
    ) -> Tuple[Dict[str, Any], ResponseMeta]:
        params: Dict[str, Any] = {}
        if page is not None:
            params["page"] = page
        if limit is not None:
            params["limit"] = limit
        if active is not None:
            params["active"] = active
        if code:
            params["code"] = code
        return self._http.request("GET", "/coupons", params=params)

    # POST /coupons
    def create(self, payload: Dict[str, Any]) -> Tuple[Dict[str, Any], ResponseMeta]:
        return self._http.request("POST", "/coupons", json_body=payload)

    # GET /coupons/{couponId}
    def get(self, coupon_id: str) -> Tuple[Dict[str, Any], ResponseMeta]:
        return self._http.request("GET", f"/coupons/{coupon_id}")

    # PATCH /coupons/{couponId}
    def update(self, coupon_id: str, payload: Dict[str, Any]) -> Tuple[Dict[str, Any], ResponseMeta]:
        return self._http.request("PATCH", f"/coupons/{coupon_id}", json_body=payload)

    # DELETE /coupons/{couponId}
    def delete(self, coupon_id: str) -> Tuple[Dict[str, Any], ResponseMeta]:
        return self._http.request("DELETE", f"/coupons/{coupon_id}")
