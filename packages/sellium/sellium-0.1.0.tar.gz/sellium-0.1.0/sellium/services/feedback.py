from __future__ import annotations

from typing import Any, Dict, Optional, Tuple
from sellium._http import HTTPClient
from sellium.types import ResponseMeta


class FeedbackService:
    def __init__(self, http: HTTPClient) -> None:
        self._http = http

    # GET /feedback
    def list(
        self,
        *,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        rating: Optional[int] = None,
        has_response: Optional[bool] = None,
        is_visible: Optional[bool] = None,
        email: Optional[str] = None,
    ) -> Tuple[Dict[str, Any], ResponseMeta]:
        params: Dict[str, Any] = {}
        if page is not None:
            params["page"] = page
        if limit is not None:
            params["limit"] = limit
        if rating is not None:
            params["rating"] = rating
        if has_response is not None:
            params["has_response"] = has_response
        if is_visible is not None:
            params["is_visible"] = is_visible
        if email:
            params["email"] = email
        return self._http.request("GET", "/feedback", params=params)

    # GET /feedback/{feedbackId}
    def get(self, feedback_id: str) -> Tuple[Dict[str, Any], ResponseMeta]:
        return self._http.request("GET", f"/feedback/{feedback_id}")

    # PATCH /feedback/{feedbackId}
    def update(self, feedback_id: str, payload: Dict[str, Any]) -> Tuple[Dict[str, Any], ResponseMeta]:
        return self._http.request("PATCH", f"/feedback/{feedback_id}", json_body=payload)
