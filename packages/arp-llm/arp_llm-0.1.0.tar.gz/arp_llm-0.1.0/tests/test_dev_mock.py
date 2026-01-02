import asyncio
import json

import pytest

from arp_llm import DevMockChatModel, DevMockEmbedder, LlmError, Message
from arp_llm.providers.dev_mock import DevMockChatFixture


def test_dev_mock_default_is_deterministic() -> None:
    async def run() -> None:
        model = DevMockChatModel(default_text="x")
        messages = [Message.user("hello"), Message.system("sys")]
        first = await model.response(messages)
        second = await model.response(messages)
        assert first.text == second.text
        assert first.text.startswith("x:")

    asyncio.run(run())


def test_dev_mock_fixtures_are_consumed_in_order() -> None:
    async def run() -> None:
        model = DevMockChatModel(fixtures=[DevMockChatFixture(text="a"), DevMockChatFixture(text="b")])
        assert (await model.response([Message.user("x")])).text == "a"
        assert (await model.response([Message.user("x")])).text == "b"
        with pytest.raises(LlmError):
            await model.response([Message.user("x")])

    asyncio.run(run())


def test_dev_mock_structured_parses_json() -> None:
    async def run() -> None:
        model = DevMockChatModel(fixtures=[DevMockChatFixture(text='{"a": 1}')])
        resp = await model.response([Message.user("x")], response_schema={"type": "object"})
        assert resp.parsed == {"a": 1}

    asyncio.run(run())


def test_dev_mock_structured_uses_fixture_parsed() -> None:
    async def run() -> None:
        model = DevMockChatModel(
            fixtures=[
                DevMockChatFixture(text="not-json", parsed={"a": 1}),
            ]
        )
        resp = await model.response([Message.assistant("x")], response_schema={"type": "object"})
        assert resp.parsed == {"a": 1}

    asyncio.run(run())


def test_dev_mock_structured_requires_object() -> None:
    async def run() -> None:
        model = DevMockChatModel(fixtures=[DevMockChatFixture(text="[1, 2]")])
        with pytest.raises(LlmError) as exc:
            await model.response([Message.user("x")], response_schema={"type": "object"})
        assert exc.value.code == "parse_error"

    asyncio.run(run())


def test_dev_mock_schema_validation_failure_raises_parse_error() -> None:
    async def run() -> None:
        model = DevMockChatModel(fixtures=[DevMockChatFixture(text="{}", parsed={})])
        with pytest.raises(LlmError) as exc:
            await model.response([Message.user("x")], response_schema={"type": "object", "required": ["a"]})
        assert exc.value.code == "parse_error"

    asyncio.run(run())


def test_dev_mock_from_env_loads_fixtures(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    async def run() -> None:
        path = tmp_path / "fixtures.json"
        path.write_text(json.dumps([{"text": "one"}, {"text": "two"}]), encoding="utf-8")
        monkeypatch.setenv("ARP_LLM_DEV_MOCK_FIXTURES_PATH", str(path))
        model = DevMockChatModel.from_env()
        assert (await model.response([Message.user("x")])).text == "one"
        assert (await model.response([Message.user("x")])).text == "two"

    asyncio.run(run())


def test_dev_mock_from_env_missing_file_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ARP_LLM_DEV_MOCK_FIXTURES_PATH", "/does/not/exist.json")
    with pytest.raises(LlmError) as exc:
        DevMockChatModel.from_env()
    assert exc.value.code == "invalid_request"


def test_dev_mock_from_env_invalid_json_raises(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    path = tmp_path / "fixtures.json"
    path.write_text("not json", encoding="utf-8")
    monkeypatch.setenv("ARP_LLM_DEV_MOCK_FIXTURES_PATH", str(path))
    with pytest.raises(LlmError) as exc:
        DevMockChatModel.from_env()
    assert exc.value.code == "invalid_request"


def test_dev_mock_from_env_invalid_shape_raises(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    path = tmp_path / "fixtures.json"
    path.write_text(json.dumps({"text": "x"}), encoding="utf-8")
    monkeypatch.setenv("ARP_LLM_DEV_MOCK_FIXTURES_PATH", str(path))
    with pytest.raises(LlmError) as exc:
        DevMockChatModel.from_env()
    assert exc.value.code == "invalid_request"


def test_dev_mock_from_env_invalid_item_raises(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    path = tmp_path / "fixtures.json"
    path.write_text(json.dumps([{"parsed": 1}]), encoding="utf-8")
    monkeypatch.setenv("ARP_LLM_DEV_MOCK_FIXTURES_PATH", str(path))
    with pytest.raises(LlmError) as exc:
        DevMockChatModel.from_env()
    assert exc.value.code == "invalid_request"


def test_dev_mock_from_env_invalid_parsed_raises(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    path = tmp_path / "fixtures.json"
    path.write_text(json.dumps([{"text": "x", "parsed": 1}]), encoding="utf-8")
    monkeypatch.setenv("ARP_LLM_DEV_MOCK_FIXTURES_PATH", str(path))
    with pytest.raises(LlmError) as exc:
        DevMockChatModel.from_env()
    assert exc.value.code == "invalid_request"


def test_dev_mock_embedder_rejects_non_positive_dimensions() -> None:
    with pytest.raises(LlmError) as exc:
        DevMockEmbedder(dimensions=0)
    assert exc.value.code == "invalid_request"


def test_dev_mock_embedder_is_deterministic() -> None:
    async def run() -> None:
        embedder = DevMockEmbedder(dimensions=4)
        first = await embedder.embed(["hello"])
        second = await embedder.embed(["hello"])
        assert first.vectors == second.vectors
        assert first.dimensions == 4

    asyncio.run(run())
