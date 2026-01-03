from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class APIError(Exception):
    status: int
    code: str = "HTTP_ERROR"
    message: str = "Request failed"
    raw: Optional[bytes] = None

    def __str__(self) -> str:
        return f"Sellium API error ({self.status}) {self.code}: {self.message}"
