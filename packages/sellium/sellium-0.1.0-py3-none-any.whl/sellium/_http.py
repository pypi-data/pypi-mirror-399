from __future__ import annotations

from typing import Any, Dict, Optional, Tuple
import json
import httpx

from .errors import APIError
from .types import ResponseMeta, parse_rate_limit


class HTTPClient:
    def __init__(
        self,
        api_key: str,
        store_id: str,
        base_url: str,
        user_agent: str,
        timeout: float = 30.0,
        client: Optional[httpx.Client] = None,
    ) -> None:
        self.api_key = api_key
        self.store_id = store_id
        self.base_url = base_url.rstrip("/")
        self.user_agent = user_agent

        self._client = client or httpx.Client(timeout=timeout)

    def close(self) -> None:
        self._client.close()

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Dict[str, Any], ResponseMeta]:
        url = f"{self.base_url}{path}"

        headers = {
            "X-API-Key": self.api_key,
            "X-Store-ID": self.store_id,
            "Accept": "application/json",
            "User-Agent": self.user_agent,
        }

        resp = self._client.request(method, url, params=params, json=json_body, headers=headers)

        meta = ResponseMeta(
            status=resp.status_code,
            headers=resp.headers,
            rate_limit=parse_rate_limit(resp.headers),
        )

        raw = resp.content or b""
        if not raw:
            if 200 <= resp.status_code < 300:
                return {}, meta
            raise APIError(status=resp.status_code, raw=raw)

        try:
            data = resp.json()
        except Exception:
            if 200 <= resp.status_code < 300:
                return {"raw": raw.decode("utf-8", errors="replace")}, meta
            raise APIError(status=resp.status_code, raw=raw)


        if isinstance(data, dict) and "success" in data:
            if data.get("success") is True:
                return data, meta

            err = data.get("error") or {}
            raise APIError(
                status=resp.status_code,
                code=str(err.get("code") or "API_ERROR"),
                message=str(err.get("message") or "Request failed"),
                raw=raw,
            )

        if 200 <= resp.status_code < 300:
            return data if isinstance(data, dict) else {"data": data}, meta

        raise APIError(status=resp.status_code, raw=raw)
