from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional
import httpx


@dataclass
class RateLimit:
    limit: int
    remaining: int
    reset_sec: int


@dataclass
class ResponseMeta:
    status: int
    headers: httpx.Headers
    rate_limit: Optional[RateLimit] = None


def parse_rate_limit(headers: httpx.Headers) -> Optional[RateLimit]:
    def _int(name: str) -> int:
        v = headers.get(name)
        try:
            return int(v) if v is not None else 0
        except ValueError:
            return 0

    limit = _int("X-RateLimit-Limit")
    remaining = _int("X-RateLimit-Remaining")
    reset_sec = _int("X-RateLimit-Reset")
    if limit == 0 and remaining == 0 and reset_sec == 0:
        return None
    return RateLimit(limit=limit, remaining=remaining, reset_sec=reset_sec)


Json = Dict[str, Any]
