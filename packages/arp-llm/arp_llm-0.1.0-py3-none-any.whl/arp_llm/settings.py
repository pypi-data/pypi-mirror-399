from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Literal, overload

from .errors import LlmError
from .types import ChatModel, Embedder

Profile = Literal["dev-mock", "openai"]


@dataclass(frozen=True)
class LlmEnv:
    profile: Profile
    chat_model: str | None
    embed_model: str | None
    api_key: str | None
    base_url: str | None
    timeout_seconds: float
    max_retries: int
    temperature: float | None


def load_chat_model_from_env_or_dev_mock() -> ChatModel:
    profile = _read_env("ARP_LLM_PROFILE", required=False) or "dev-mock"
    if profile == "dev-mock":
        from .providers.dev_mock import DevMockChatModel

        return DevMockChatModel.from_env()
    return load_chat_model_from_env()


def load_chat_model_from_env() -> ChatModel:
    env = _env_from_os()
    if env.profile == "dev-mock":
        from .providers.dev_mock import DevMockChatModel

        return DevMockChatModel.from_env()
    if env.profile == "openai":
        from .providers.openai import OpenAIChatModel

        if (model := env.chat_model) is None:
            raise LlmError(code="invalid_request", message="Missing required env var: ARP_LLM_CHAT_MODEL")
        if (api_key := env.api_key) is None:
            raise LlmError(code="auth_error", message="Missing required env var: ARP_LLM_API_KEY")
        return OpenAIChatModel(
            model=model,
            api_key=api_key,
            base_url=env.base_url,
            timeout_seconds=env.timeout_seconds,
            max_retries=env.max_retries,
            default_temperature=env.temperature,
        )
    raise LlmError(code="invalid_request", message=f"Unsupported ARP_LLM_PROFILE: {env.profile}")  # pragma: no cover


def load_embedder_from_env_or_dev_mock() -> Embedder:
    profile = _read_env("ARP_LLM_PROFILE", required=False) or "dev-mock"
    if profile == "dev-mock":
        from .providers.dev_mock import DevMockEmbedder

        return DevMockEmbedder()
    return load_embedder_from_env()


def load_embedder_from_env() -> Embedder:
    env = _env_from_os()
    if env.profile == "dev-mock":
        from .providers.dev_mock import DevMockEmbedder

        return DevMockEmbedder()
    if env.profile == "openai":
        from .providers.openai import OpenAIEmbedder

        if (model := env.embed_model) is None:
            raise LlmError(code="invalid_request", message="Missing required env var: ARP_LLM_EMBED_MODEL")
        if (api_key := env.api_key) is None:
            raise LlmError(code="auth_error", message="Missing required env var: ARP_LLM_API_KEY")
        return OpenAIEmbedder(
            model=model,
            api_key=api_key,
            base_url=env.base_url,
            timeout_seconds=env.timeout_seconds,
            max_retries=env.max_retries,
        )
    raise LlmError(code="invalid_request", message=f"Unsupported ARP_LLM_PROFILE: {env.profile}")  # pragma: no cover


def _env_from_os() -> LlmEnv:
    profile = _read_env("ARP_LLM_PROFILE", required=True)
    if profile not in ("dev-mock", "openai"):
        raise LlmError(code="invalid_request", message=f"Unsupported ARP_LLM_PROFILE: {profile}")

    chat_model = _read_env("ARP_LLM_CHAT_MODEL", required=False)
    embed_model = _read_env("ARP_LLM_EMBED_MODEL", required=False)
    api_key = _read_env("ARP_LLM_API_KEY", required=False)
    base_url = _read_env("ARP_LLM_BASE_URL", required=False)

    timeout_seconds = _read_env("ARP_LLM_TIMEOUT_SECONDS", required=False)
    timeout = 30.0
    if timeout_seconds:
        timeout = _as_float(timeout_seconds, name="ARP_LLM_TIMEOUT_SECONDS")

    max_retries_raw = _read_env("ARP_LLM_MAX_RETRIES", required=False)
    max_retries = 2
    if max_retries_raw:
        max_retries = _as_int(max_retries_raw, name="ARP_LLM_MAX_RETRIES")

    temperature_raw = _read_env("ARP_LLM_TEMPERATURE", required=False)
    temperature = _as_float(temperature_raw, name="ARP_LLM_TEMPERATURE") if temperature_raw else None

    return LlmEnv(
        profile=profile,
        chat_model=chat_model,
        embed_model=embed_model,
        api_key=api_key,
        base_url=base_url,
        timeout_seconds=timeout,
        max_retries=max_retries,
        temperature=temperature,
    )


@overload
def _read_env(name: str, *, required: Literal[True]) -> str:
    ...


@overload
def _read_env(name: str, *, required: Literal[False]) -> str | None:
    ...


def _read_env(name: str, *, required: bool) -> str | None:
    value = os.environ.get(name)
    if value is None or not value.strip():
        if required:
            raise LlmError(code="invalid_request", message=f"Missing required env var: {name}")
        return None
    return value.strip()


def _as_float(raw: str, *, name: str) -> float:
    try:
        return float(raw)
    except ValueError as exc:
        raise LlmError(code="invalid_request", message=f"{name} must be a number") from exc


def _as_int(raw: str, *, name: str) -> int:
    try:
        return int(raw)
    except ValueError as exc:
        raise LlmError(code="invalid_request", message=f"{name} must be an integer") from exc
