from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Literal, Mapping, Sequence

JsonObject = dict[str, Any]
JsonSchema = Mapping[str, Any]
Metadata = Mapping[str, Any]

MessageRole = Literal["system", "user", "assistant"]


@dataclass(frozen=True)
class Message:
    role: MessageRole
    content: str

    @classmethod
    def system(cls, content: str) -> "Message":
        return cls(role="system", content=content)

    @classmethod
    def user(cls, content: str) -> "Message":
        return cls(role="user", content=content)

    @classmethod
    def assistant(cls, content: str) -> "Message":
        return cls(role="assistant", content=content)


@dataclass(frozen=True)
class Response:
    text: str
    parsed: JsonObject | None
    usage: dict[str, Any] | None
    provider: str
    model: str
    request_id: str | None
    latency_ms: int


@dataclass(frozen=True)
class EmbeddingResponse:
    vectors: list[list[float]]
    dimensions: int
    usage: dict[str, Any] | None
    provider: str
    model: str
    request_id: str | None
    latency_ms: int


class ChatModel(ABC):
    @abstractmethod
    async def response(
        self,
        messages: Sequence[Message],
        *,
        response_schema: JsonSchema | None = None,
        temperature: float | None = None,
        timeout_seconds: float | None = None,
        metadata: Metadata | None = None,
    ) -> Response:
        raise NotImplementedError


class Embedder(ABC):
    @abstractmethod
    async def embed(
        self,
        texts: Sequence[str],
        *,
        timeout_seconds: float | None = None,
        metadata: Metadata | None = None,
    ) -> EmbeddingResponse:
        raise NotImplementedError
