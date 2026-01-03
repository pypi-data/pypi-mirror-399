from __future__ import annotations

import asyncio
import hashlib
import json
import os
import time
from dataclasses import dataclass
from typing import Any, Sequence

from ..errors import LlmError
from ..json_utils import extract_json
from ..types import ChatModel, EmbeddingResponse, Embedder, JsonObject, JsonSchema, Message, Metadata, Response


@dataclass(frozen=True)
class DevMockChatFixture:
    text: str
    parsed: JsonObject | None = None


class DevMockChatModel(ChatModel):
    """Deterministic, no-network ChatModel for unit tests and offline development."""

    def __init__(
        self,
        *,
        fixtures: Sequence[DevMockChatFixture] | None = None,
        default_text: str = "dev-mock",
    ) -> None:
        self._fixtures = list(fixtures) if fixtures is not None else None
        self._default_text = default_text
        self._index = 0
        self._lock = asyncio.Lock()

    @classmethod
    def from_env(cls) -> "DevMockChatModel":
        path = os.environ.get("ARP_LLM_DEV_MOCK_FIXTURES_PATH")
        if not path:
            return cls()
        try:
            with open(path, "rb") as handle:
                payload = json.load(handle)
        except OSError as exc:
            raise LlmError(code="invalid_request", message="Failed to read dev mock fixtures file") from exc
        except json.JSONDecodeError as exc:
            raise LlmError(code="invalid_request", message="Dev mock fixtures file was not valid JSON") from exc
        if not isinstance(payload, list):
            raise LlmError(code="invalid_request", message="Dev mock fixtures file must be a JSON array")

        fixtures: list[DevMockChatFixture] = []
        for item in payload:
            if not isinstance(item, dict):
                raise LlmError(code="invalid_request", message="Each dev mock fixture must be a JSON object")
            text = item.get("text")
            if not isinstance(text, str):
                raise LlmError(code="invalid_request", message="Dev mock fixture missing 'text' string")
            parsed = item.get("parsed")
            if parsed is not None and not isinstance(parsed, dict):
                raise LlmError(code="invalid_request", message="Dev mock fixture 'parsed' must be a JSON object")
            fixtures.append(DevMockChatFixture(text=text, parsed=parsed))
        return cls(fixtures=fixtures)

    async def response(
        self,
        messages: Sequence[Message],
        *,
        response_schema: JsonSchema | None = None,
        temperature: float | None = None,
        timeout_seconds: float | None = None,
        metadata: Metadata | None = None,
    ) -> Response:
        _ = temperature, timeout_seconds, metadata

        start = time.perf_counter()
        fixture = await self._next_fixture()

        text = fixture.text if fixture else self._default_text_from_messages(messages)
        parsed: JsonObject | None = None

        if response_schema is not None:
            if fixture and fixture.parsed is not None:
                parsed = fixture.parsed
            else:
                value = extract_json(text)
                if not isinstance(value, dict):
                    raise LlmError(
                        code="parse_error",
                        message="Structured response must be a JSON object",
                        details={"text": text},
                    )
                parsed = value
            _validate_json_schema_if_available(parsed, response_schema)

        latency_ms = int((time.perf_counter() - start) * 1000)
        return Response(
            text=text,
            parsed=parsed,
            usage={"dev_mock": True},
            provider="dev-mock",
            model="dev-mock",
            request_id=None,
            latency_ms=latency_ms,
        )

    async def _next_fixture(self) -> DevMockChatFixture | None:
        if self._fixtures is None:
            return None
        async with self._lock:
            if self._index >= len(self._fixtures):
                raise LlmError(
                    code="invalid_request",
                    message="Dev mock fixtures exhausted",
                    details={"fixtures": len(self._fixtures)},
                )
            fixture = self._fixtures[self._index]
            self._index += 1
            return fixture

    def _default_text_from_messages(self, messages: Sequence[Message]) -> str:
        hasher = hashlib.sha256()
        for msg in messages:
            hasher.update(msg.role.encode("utf-8"))
            hasher.update(b"\n")
            hasher.update(msg.content.encode("utf-8"))
            hasher.update(b"\n\n")
        return f"{self._default_text}:{hasher.hexdigest()[:16]}"


class DevMockEmbedder(Embedder):
    """Deterministic, no-network Embedder for unit tests and offline development."""

    def __init__(self, *, dimensions: int = 8) -> None:
        if dimensions <= 0:
            raise LlmError(code="invalid_request", message="dimensions must be > 0")
        self._dimensions = dimensions

    async def embed(
        self,
        texts: Sequence[str],
        *,
        timeout_seconds: float | None = None,
        metadata: Metadata | None = None,
    ) -> EmbeddingResponse:
        _ = timeout_seconds, metadata

        start = time.perf_counter()
        vectors: list[list[float]] = [self._vector_for_text(text) for text in texts]
        latency_ms = int((time.perf_counter() - start) * 1000)
        return EmbeddingResponse(
            vectors=vectors,
            dimensions=self._dimensions,
            usage={"dev_mock": True},
            provider="dev-mock",
            model="dev-mock",
            request_id=None,
            latency_ms=latency_ms,
        )

    def _vector_for_text(self, text: str) -> list[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        values: list[float] = []
        for index in range(self._dimensions):
            byte = digest[index % len(digest)]
            values.append((byte / 255.0) * 2.0 - 1.0)
        return values


def _validate_json_schema_if_available(instance: JsonObject, schema: JsonSchema) -> None:
    try:
        import jsonschema  # type: ignore[import-not-found]
    except ImportError:  # pragma: no cover
        return
    try:
        jsonschema.validate(instance=instance, schema=schema)
    except Exception as exc:
        raise LlmError(
            code="parse_error",
            message="Structured response did not match JSON Schema",
            details={"error": str(exc)},
        ) from exc
