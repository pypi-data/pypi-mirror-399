import os

import pytest

from arp_llm import LlmError, load_chat_model_from_env, load_chat_model_from_env_or_dev_mock, load_embedder_from_env
from arp_llm.providers.dev_mock import DevMockChatModel
from arp_llm.providers.openai import OpenAIChatModel, OpenAIEmbedder


def test_load_chat_model_from_env_or_dev_mock_defaults_to_dev_mock(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ARP_LLM_PROFILE", raising=False)
    model = load_chat_model_from_env_or_dev_mock()
    assert isinstance(model, DevMockChatModel)


def test_load_chat_model_from_env_requires_profile(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ARP_LLM_PROFILE", raising=False)
    with pytest.raises(LlmError) as exc:
        load_chat_model_from_env()
    assert exc.value.code == "invalid_request"


def test_openai_compatible_requires_chat_model(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ARP_LLM_PROFILE", "openai")
    monkeypatch.setenv("ARP_LLM_API_KEY", "k")
    monkeypatch.delenv("ARP_LLM_CHAT_MODEL", raising=False)
    with pytest.raises(LlmError) as exc:
        load_chat_model_from_env()
    assert exc.value.code == "invalid_request"


def test_openai_compatible_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ARP_LLM_PROFILE", "openai")
    monkeypatch.setenv("ARP_LLM_CHAT_MODEL", "m")
    monkeypatch.delenv("ARP_LLM_API_KEY", raising=False)
    with pytest.raises(LlmError) as exc:
        load_chat_model_from_env()
    assert exc.value.code == "auth_error"


def test_openai_compatible_embedder_requires_embed_model(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ARP_LLM_PROFILE", "openai")
    monkeypatch.setenv("ARP_LLM_API_KEY", "k")
    monkeypatch.delenv("ARP_LLM_EMBED_MODEL", raising=False)
    with pytest.raises(LlmError) as exc:
        load_embedder_from_env()
    assert exc.value.code == "invalid_request"


def test_openai_compatible_timeout_parsing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ARP_LLM_PROFILE", "openai")
    monkeypatch.setenv("ARP_LLM_CHAT_MODEL", "m")
    monkeypatch.setenv("ARP_LLM_API_KEY", "k")
    monkeypatch.setenv("ARP_LLM_TIMEOUT_SECONDS", "12.5")
    model = load_chat_model_from_env()
    assert getattr(model, "_timeout_seconds", None) == 12.5  # implementation detail


def test_openai_compatible_max_retries_parsing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ARP_LLM_PROFILE", "openai")
    monkeypatch.setenv("ARP_LLM_CHAT_MODEL", "m")
    monkeypatch.setenv("ARP_LLM_API_KEY", "k")
    monkeypatch.setenv("ARP_LLM_MAX_RETRIES", "3")
    model = load_chat_model_from_env()
    assert getattr(model, "_max_retries", None) == 3  # implementation detail


def test_load_chat_model_from_env_or_dev_mock_respects_profile(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ARP_LLM_PROFILE", "openai")
    monkeypatch.setenv("ARP_LLM_CHAT_MODEL", "m")
    monkeypatch.setenv("ARP_LLM_API_KEY", "k")
    model = load_chat_model_from_env_or_dev_mock()
    assert isinstance(model, OpenAIChatModel)


def test_load_embedder_from_env_or_dev_mock_respects_profile(monkeypatch: pytest.MonkeyPatch) -> None:
    from arp_llm import load_embedder_from_env_or_dev_mock

    monkeypatch.setenv("ARP_LLM_PROFILE", "openai")
    monkeypatch.setenv("ARP_LLM_EMBED_MODEL", "e")
    monkeypatch.setenv("ARP_LLM_API_KEY", "k")
    embedder = load_embedder_from_env_or_dev_mock()
    assert isinstance(embedder, OpenAIEmbedder)


def test_invalid_profile_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ARP_LLM_PROFILE", "bogus")
    with pytest.raises(LlmError) as exc:
        load_chat_model_from_env()
    assert exc.value.code == "invalid_request"


def test_invalid_timeout_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ARP_LLM_PROFILE", "openai")
    monkeypatch.setenv("ARP_LLM_CHAT_MODEL", "m")
    monkeypatch.setenv("ARP_LLM_API_KEY", "k")
    monkeypatch.setenv("ARP_LLM_TIMEOUT_SECONDS", "nope")
    with pytest.raises(LlmError) as exc:
        load_chat_model_from_env()
    assert exc.value.code == "invalid_request"


def test_invalid_max_retries_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ARP_LLM_PROFILE", "openai")
    monkeypatch.setenv("ARP_LLM_CHAT_MODEL", "m")
    monkeypatch.setenv("ARP_LLM_API_KEY", "k")
    monkeypatch.setenv("ARP_LLM_MAX_RETRIES", "nope")
    with pytest.raises(LlmError) as exc:
        load_chat_model_from_env()
    assert exc.value.code == "invalid_request"


def test_env_helpers_do_not_leak_os_environ(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ARP_LLM_PROFILE", "dev-mock")
    model = load_chat_model_from_env()
    assert isinstance(model, DevMockChatModel)
    assert "ARP_LLM_PROFILE" in os.environ
