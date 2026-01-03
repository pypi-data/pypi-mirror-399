from __future__ import annotations

import time
from collections.abc import Awaitable
from typing import Any, NoReturn, Sequence

import openai

from ..errors import LlmError
from ..json_utils import extract_json
from ..types import ChatModel, EmbeddingResponse, Embedder, JsonObject, JsonSchema, Message, Metadata, Response


class OpenAIChatModel(ChatModel):
    """OpenAI Responses API client (SDK-backed)."""

    def __init__(
        self,
        *,
        model: str,
        api_key: str,
        base_url: str | None = None,
        timeout_seconds: float = 30.0,
        max_retries: int = 2,
        default_temperature: float | None = None,
        client: Any | None = None,
    ) -> None:
        self._model = model
        self._api_key = api_key
        self._base_url = base_url
        self._timeout_seconds = timeout_seconds
        self._max_retries = max_retries
        self._default_temperature = default_temperature

        self._client = client
        self._owns_client = client is None

    async def aclose(self) -> None:
        if self._owns_client and self._client is not None:
            close = getattr(self._client, "close", None)
            if callable(close):
                result = close()
                if isinstance(result, Awaitable):
                    await result

    async def response(
        self,
        messages: Sequence[Message],
        *,
        response_schema: JsonSchema | None = None,
        temperature: float | None = None,
        timeout_seconds: float | None = None,
        metadata: Metadata | None = None,
    ) -> Response:
        _ = metadata

        start = time.perf_counter()
        timeout = timeout_seconds if timeout_seconds is not None else self._timeout_seconds
        resolved_temp = temperature if temperature is not None else self._default_temperature
        client = await self._get_or_create_client()

        kwargs: dict[str, Any] = {
            "model": self._model,
            "input": [{"role": msg.role, "content": msg.content} for msg in messages],
            "timeout": timeout,
        }
        if resolved_temp is not None:
            kwargs["temperature"] = resolved_temp
        if response_schema is not None:
            kwargs["text"] = {
                "format": {
                    "type": "json_schema",
                    "name": "arp_llm_response",
                    "schema": dict(response_schema),
                    "strict": True,
                }
            }

        try:
            resp = await client.responses.parse(**kwargs)
        except LlmError:
            raise
        except Exception as exc:
            _raise_llm_error_from_openai_exception(exc)

        request_id = _as_str(getattr(resp, "id", None))
        text = getattr(resp, "output_text", None)
        if not isinstance(text, str):
            raise LlmError(code="provider_error", message="OpenAI response missing output_text")

        parsed: JsonObject | None = None
        if response_schema is not None:
            output_parsed = _maybe_model_to_dict(getattr(resp, "output_parsed", None))
            if isinstance(output_parsed, dict):
                parsed = output_parsed
            else:
                value = extract_json(text)
                if not isinstance(value, dict):
                    raise LlmError(
                        code="parse_error",
                        message="Structured response must be a JSON object",
                        details={"text": text, "request_id": request_id},
                    )
                parsed = value
            _validate_json_schema_if_available(parsed, response_schema)

        usage = _maybe_model_to_dict(getattr(resp, "usage", None))
        latency_ms = int((time.perf_counter() - start) * 1000)
        return Response(
            text=text,
            parsed=parsed,
            usage=usage if isinstance(usage, dict) else None,
            provider="openai",
            model=self._model,
            request_id=request_id,
            latency_ms=latency_ms,
        )

    async def _get_or_create_client(self) -> Any:
        if self._client is not None:
            return self._client
        AsyncOpenAI = getattr(openai, "AsyncOpenAI", None)
        if AsyncOpenAI is None:
            raise LlmError(code="invalid_request", message="Unsupported OpenAI SDK version: missing AsyncOpenAI")
        self._client = AsyncOpenAI(
            api_key=self._api_key,
            base_url=_normalize_openai_base_url(self._base_url),
            timeout=self._timeout_seconds,
            max_retries=self._max_retries,
            _strict_response_validation=True,
        )
        return self._client


class OpenAIEmbedder(Embedder):
    """OpenAI embeddings client (SDK-backed)."""

    def __init__(
        self,
        *,
        model: str,
        api_key: str,
        base_url: str | None = None,
        timeout_seconds: float = 30.0,
        max_retries: int = 2,
        client: Any | None = None,
    ) -> None:
        self._model = model
        self._api_key = api_key
        self._base_url = base_url
        self._timeout_seconds = timeout_seconds
        self._max_retries = max_retries

        self._client = client
        self._owns_client = client is None

    async def aclose(self) -> None:
        if self._owns_client and self._client is not None:
            close = getattr(self._client, "close", None)
            if callable(close):
                result = close()
                if isinstance(result, Awaitable):
                    await result

    async def embed(
        self,
        texts: Sequence[str],
        *,
        timeout_seconds: float | None = None,
        metadata: Metadata | None = None,
    ) -> EmbeddingResponse:
        _ = metadata

        start = time.perf_counter()
        timeout = timeout_seconds if timeout_seconds is not None else self._timeout_seconds
        client = await self._get_or_create_client()

        try:
            resp = await client.embeddings.create(model=self._model, input=list(texts), timeout=timeout)
        except LlmError:
            raise
        except Exception as exc:
            _raise_llm_error_from_openai_exception(exc)

        request_id = _as_str(getattr(resp, "id", None))
        data = getattr(resp, "data", None)
        if not isinstance(data, list):
            raise LlmError(code="provider_error", message="OpenAI embeddings response missing data")

        vectors: list[list[float]] = []
        for item in data:
            embedding = getattr(item, "embedding", None)
            if not isinstance(embedding, list) or not all(isinstance(x, (int, float)) for x in embedding):
                raise LlmError(code="provider_error", message="OpenAI embeddings response item missing embedding vector")
            vectors.append([float(x) for x in embedding])

        usage = _maybe_model_to_dict(getattr(resp, "usage", None))
        latency_ms = int((time.perf_counter() - start) * 1000)
        dimensions = len(vectors[0]) if vectors else 0
        return EmbeddingResponse(
            vectors=vectors,
            dimensions=dimensions,
            usage=usage if isinstance(usage, dict) else None,
            provider="openai",
            model=self._model,
            request_id=request_id,
            latency_ms=latency_ms,
        )

    async def _get_or_create_client(self) -> Any:
        if self._client is not None:
            return self._client
        AsyncOpenAI = getattr(openai, "AsyncOpenAI", None)
        if AsyncOpenAI is None:
            raise LlmError(code="invalid_request", message="Unsupported OpenAI SDK version: missing AsyncOpenAI")
        self._client = AsyncOpenAI(
            api_key=self._api_key,
            base_url=_normalize_openai_base_url(self._base_url),
            timeout=self._timeout_seconds,
            max_retries=self._max_retries,
            _strict_response_validation=True,
        )
        return self._client


def _as_str(value: Any) -> str | None:
    return value if isinstance(value, str) else None


def _maybe_model_to_dict(obj: Any) -> Any:
    if obj is None:
        return None
    model_dump = getattr(obj, "model_dump", None)
    if callable(model_dump):
        return model_dump()
    as_dict = getattr(obj, "dict", None)
    if callable(as_dict):
        return as_dict()
    return obj


def _normalize_openai_base_url(base_url: str | None) -> str:
    resolved = (base_url or "https://api.openai.com/v1").rstrip("/")
    return resolved if resolved.endswith("/v1") else f"{resolved}/v1"


def _raise_llm_error_from_openai_exception(exc: Exception) -> NoReturn:
    status_code = getattr(exc, "status_code", None)
    request_id = getattr(exc, "request_id", None)
    details = {"request_id": request_id} if request_id else None

    if isinstance(exc, (openai.AuthenticationError, openai.PermissionDeniedError)):
        raise LlmError(code="auth_error", message="OpenAI authentication failed", status_code=status_code, details=details)
    if isinstance(exc, openai.RateLimitError):
        raise LlmError(
            code="rate_limited",
            message="OpenAI rate limited the request",
            retryable=True,
            status_code=status_code,
            details=details,
        )
    if isinstance(exc, openai.APITimeoutError):
        raise LlmError(code="timeout", message="OpenAI request timed out", retryable=True, status_code=status_code)
    if isinstance(exc, openai.APIConnectionError):
        raise LlmError(code="provider_error", message="OpenAI connection error", retryable=True, status_code=status_code)
    if isinstance(exc, (openai.BadRequestError, openai.UnprocessableEntityError)):
        raise LlmError(code="invalid_request", message="OpenAI rejected the request", status_code=status_code, details=details)

    if isinstance(exc, openai.APIError):
        retryable = bool(status_code and int(status_code) >= 500)
        raise LlmError(
            code="provider_error",
            message="OpenAI provider error",
            retryable=retryable,
            status_code=status_code,
            details=details,
        )

    raise LlmError(code="provider_error", message="OpenAI request failed", status_code=status_code, details=details) from exc


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
