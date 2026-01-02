from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

LlmErrorCode = Literal[
    "invalid_request",
    "auth_error",
    "rate_limited",
    "timeout",
    "provider_error",
    "parse_error",
]


@dataclass(frozen=True)
class LlmError(Exception):
    code: LlmErrorCode
    message: str
    retryable: bool = False
    status_code: int | None = None
    details: dict[str, Any] | None = None

    def __str__(self) -> str:  # pragma: no cover
        return self.message

