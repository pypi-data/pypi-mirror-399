import asyncio
from typing import Any

import httpx
import openai
import pytest

from arp_llm import LlmError, Message
from arp_llm.providers import openai as openai_provider
from arp_llm.providers.openai import OpenAIChatModel, OpenAIEmbedder


class _FakeParsedResponse:
    def __init__(
        self,
        *,
        output_text: object,
        output_parsed: object | None = None,
        usage: object | None = None,
        id: str | None = None,
    ) -> None:
        self.output_text = output_text
        self.output_parsed = output_parsed
        self.usage = usage
        self.id = id


class _FakeEmbeddingItem:
    def __init__(self, embedding: object) -> None:
        self.embedding = embedding


class _FakeEmbeddingResponse:
    def __init__(self, *, data: object, usage: object | None = None, id: str | None = None) -> None:
        self.data = data
        self.usage = usage
        self.id = id


class _FakeResponses:
    def __init__(self, handler) -> None:
        self._handler = handler

    async def parse(self, **kwargs):
        return self._handler(kwargs)


class _FakeEmbeddings:
    def __init__(self, handler) -> None:
        self._handler = handler

    async def create(self, **kwargs):
        return self._handler(kwargs)


class _FakeOpenAIClient:
    def __init__(self, *, responses_handler, embeddings_handler) -> None:
        self.responses = _FakeResponses(responses_handler)
        self.embeddings = _FakeEmbeddings(embeddings_handler)
        self.closed = False

    async def close(self) -> None:
        self.closed = True


class _FakeModelDump:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def model_dump(self) -> dict:
        return self._payload


class _FakeDict:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def dict(self) -> dict:
        return self._payload


def test_openai_chat_calls_responses_parse() -> None:
    def responses_handler(kwargs):
        assert kwargs["model"] == "m"
        assert kwargs["input"][0]["role"] == "user"
        assert kwargs["temperature"] == 0.25
        assert kwargs["timeout"] == 12.0
        assert "text" not in kwargs
        return _FakeParsedResponse(output_text="hello", usage={"total_tokens": 3}, id="r1")

    def embeddings_handler(_kwargs):
        raise AssertionError("not used")

    async def run() -> None:
        client = _FakeOpenAIClient(responses_handler=responses_handler, embeddings_handler=embeddings_handler)
        model = OpenAIChatModel(model="m", api_key="k", client=client)
        resp = await model.response([Message.user("hi")], temperature=0.25, timeout_seconds=12.0)
        assert resp.text == "hello"
        assert resp.parsed is None
        assert resp.usage == {"total_tokens": 3}
        assert resp.provider == "openai"
        assert resp.model == "m"
        assert resp.request_id == "r1"

    asyncio.run(run())


def test_openai_chat_structured_uses_output_parsed() -> None:
    def responses_handler(kwargs):
        assert kwargs["text"]["format"]["type"] == "json_schema"
        assert kwargs["text"]["format"]["schema"] == {"type": "object"}
        return _FakeParsedResponse(output_text="ignored", output_parsed={"a": 1}, id="r2")

    def embeddings_handler(_kwargs):
        raise AssertionError("not used")

    async def run() -> None:
        client = _FakeOpenAIClient(responses_handler=responses_handler, embeddings_handler=embeddings_handler)
        model = OpenAIChatModel(model="m", api_key="k", client=client)
        resp = await model.response([Message.user("hi")], response_schema={"type": "object"})
        assert resp.parsed == {"a": 1}

    asyncio.run(run())


def test_openai_chat_structured_falls_back_to_text_parse() -> None:
    def responses_handler(_kwargs):
        return _FakeParsedResponse(output_text='{"a": 1}', output_parsed=None, id="r3")

    def embeddings_handler(_kwargs):
        raise AssertionError("not used")

    async def run() -> None:
        client = _FakeOpenAIClient(responses_handler=responses_handler, embeddings_handler=embeddings_handler)
        model = OpenAIChatModel(model="m", api_key="k", client=client)
        resp = await model.response([Message.user("hi")], response_schema={"type": "object"})
        assert resp.parsed == {"a": 1}

    asyncio.run(run())


def test_openai_chat_structured_requires_object() -> None:
    def responses_handler(_kwargs):
        return _FakeParsedResponse(output_text="[1]", output_parsed=None, id="r4")

    def embeddings_handler(_kwargs):
        raise AssertionError("not used")

    async def run() -> None:
        client = _FakeOpenAIClient(responses_handler=responses_handler, embeddings_handler=embeddings_handler)
        model = OpenAIChatModel(model="m", api_key="k", client=client)
        with pytest.raises(LlmError) as exc:
            await model.response([Message.user("hi")], response_schema={"type": "object"})
        assert exc.value.code == "parse_error"

    asyncio.run(run())


def test_openai_chat_maps_rate_limit_error() -> None:
    def responses_handler(_kwargs):
        response = httpx.Response(429, request=httpx.Request("POST", "https://example.test"))
        raise openai.RateLimitError("rl", response=response, body=None)

    def embeddings_handler(_kwargs):
        raise AssertionError("not used")

    async def run() -> None:
        client = _FakeOpenAIClient(responses_handler=responses_handler, embeddings_handler=embeddings_handler)
        model = OpenAIChatModel(model="m", api_key="k", client=client)
        with pytest.raises(LlmError) as exc:
            await model.response([Message.user("hi")])
        assert exc.value.code == "rate_limited"
        assert exc.value.retryable is True

    asyncio.run(run())


def test_openai_chat_maps_auth_error() -> None:
    def responses_handler(_kwargs):
        response = httpx.Response(401, request=httpx.Request("POST", "https://example.test"))
        raise openai.AuthenticationError("nope", response=response, body=None)

    def embeddings_handler(_kwargs):
        raise AssertionError("not used")

    async def run() -> None:
        client = _FakeOpenAIClient(responses_handler=responses_handler, embeddings_handler=embeddings_handler)
        model = OpenAIChatModel(model="m", api_key="k", client=client)
        with pytest.raises(LlmError) as exc:
            await model.response([Message.user("hi")])
        assert exc.value.code == "auth_error"

    asyncio.run(run())


def test_openai_chat_maps_timeout_error() -> None:
    def responses_handler(_kwargs):
        request = httpx.Request("POST", "https://example.test")
        raise openai.APITimeoutError(request)

    def embeddings_handler(_kwargs):
        raise AssertionError("not used")

    async def run() -> None:
        client = _FakeOpenAIClient(responses_handler=responses_handler, embeddings_handler=embeddings_handler)
        model = OpenAIChatModel(model="m", api_key="k", client=client)
        with pytest.raises(LlmError) as exc:
            await model.response([Message.user("hi")])
        assert exc.value.code == "timeout"
        assert exc.value.retryable is True

    asyncio.run(run())


def test_openai_embedder_happy_path() -> None:
    def responses_handler(_kwargs):
        raise AssertionError("not used")

    def embeddings_handler(kwargs):
        assert kwargs["model"] == "e"
        assert kwargs["input"] == ["a", "b"]
        assert kwargs["timeout"] == 7.0
        return _FakeEmbeddingResponse(
            id="emb-1",
            data=[_FakeEmbeddingItem([0.0, 1.0]), _FakeEmbeddingItem([2.0, 3.0])],
            usage={"total_tokens": 2},
        )

    async def run() -> None:
        client = _FakeOpenAIClient(responses_handler=responses_handler, embeddings_handler=embeddings_handler)
        embedder = OpenAIEmbedder(model="e", api_key="k", client=client)
        resp = await embedder.embed(["a", "b"], timeout_seconds=7.0)
        assert resp.vectors == [[0.0, 1.0], [2.0, 3.0]]
        assert resp.dimensions == 2
        assert resp.provider == "openai"
        assert resp.request_id == "emb-1"

    asyncio.run(run())


def test_openai_chat_passthrough_llm_error() -> None:
    def responses_handler(_kwargs):
        raise LlmError(code="invalid_request", message="nope")

    def embeddings_handler(_kwargs):
        raise AssertionError("not used")

    async def run() -> None:
        client = _FakeOpenAIClient(responses_handler=responses_handler, embeddings_handler=embeddings_handler)
        model = OpenAIChatModel(model="m", api_key="k", client=client)
        with pytest.raises(LlmError) as exc:
            await model.response([Message.user("hi")])
        assert exc.value.code == "invalid_request"

    asyncio.run(run())


def test_openai_embedder_passthrough_llm_error() -> None:
    def responses_handler(_kwargs):
        raise AssertionError("not used")

    def embeddings_handler(_kwargs):
        raise LlmError(code="invalid_request", message="nope")

    async def run() -> None:
        client = _FakeOpenAIClient(responses_handler=responses_handler, embeddings_handler=embeddings_handler)
        embedder = OpenAIEmbedder(model="e", api_key="k", client=client)
        with pytest.raises(LlmError) as exc:
            await embedder.embed(["a"])
        assert exc.value.code == "invalid_request"

    asyncio.run(run())


def test_openai_chat_missing_output_text_is_error() -> None:
    def responses_handler(_kwargs):
        return _FakeParsedResponse(output_text=None, id="r-missing")

    def embeddings_handler(_kwargs):
        raise AssertionError("not used")

    async def run() -> None:
        client = _FakeOpenAIClient(responses_handler=responses_handler, embeddings_handler=embeddings_handler)
        model = OpenAIChatModel(model="m", api_key="k", client=client)
        with pytest.raises(LlmError) as exc:
            await model.response([Message.user("hi")])
        assert exc.value.code == "provider_error"

    asyncio.run(run())


def test_openai_chat_model_dump_and_dict_conversions() -> None:
    def responses_handler(_kwargs):
        return _FakeParsedResponse(
            output_text="ignored",
            output_parsed=_FakeModelDump({"a": 1}),
            usage=_FakeDict({"total_tokens": 9}),
            id="r-md",
        )

    def embeddings_handler(_kwargs):
        raise AssertionError("not used")

    async def run() -> None:
        client = _FakeOpenAIClient(responses_handler=responses_handler, embeddings_handler=embeddings_handler)
        model = OpenAIChatModel(model="m", api_key="k", client=client)
        resp = await model.response([Message.user("hi")], response_schema={"type": "object"})
        assert resp.parsed == {"a": 1}
        assert resp.usage == {"total_tokens": 9}

    asyncio.run(run())


def test_openai_embedder_missing_data_is_error() -> None:
    def responses_handler(_kwargs):
        raise AssertionError("not used")

    def embeddings_handler(_kwargs):
        return _FakeEmbeddingResponse(id="emb-missing", data=None)

    async def run() -> None:
        client = _FakeOpenAIClient(responses_handler=responses_handler, embeddings_handler=embeddings_handler)
        embedder = OpenAIEmbedder(model="e", api_key="k", client=client)
        with pytest.raises(LlmError) as exc:
            await embedder.embed(["a"])
        assert exc.value.code == "provider_error"

    asyncio.run(run())


def test_openai_embedder_missing_vector_is_error() -> None:
    def responses_handler(_kwargs):
        raise AssertionError("not used")

    def embeddings_handler(_kwargs):
        return _FakeEmbeddingResponse(id="emb-bad", data=[_FakeEmbeddingItem(embedding="bad")])

    async def run() -> None:
        client = _FakeOpenAIClient(responses_handler=responses_handler, embeddings_handler=embeddings_handler)
        embedder = OpenAIEmbedder(model="e", api_key="k", client=client)
        with pytest.raises(LlmError) as exc:
            await embedder.embed(["a"])
        assert exc.value.code == "provider_error"

    asyncio.run(run())


def test_openai_creates_client_normalizes_base_url_and_closes(monkeypatch: pytest.MonkeyPatch) -> None:
    created: list[Any] = []

    class _FakeResponsesAPI:
        async def parse(self, **_kwargs):
            return _FakeParsedResponse(output_text="ok")

    class _FakeEmbeddingsAPI:
        async def create(self, **_kwargs):
            return _FakeEmbeddingResponse(data=[], id="emb-ok")

    class _FakeAsyncOpenAI:
        def __init__(self, **kwargs) -> None:
            self.kwargs = kwargs
            self.responses = _FakeResponsesAPI()
            self.embeddings = _FakeEmbeddingsAPI()
            self.closed = False
            created.append(self)

        async def close(self) -> None:
            self.closed = True

    monkeypatch.setattr(openai_provider.openai, "AsyncOpenAI", _FakeAsyncOpenAI)

    async def run() -> None:
        model = OpenAIChatModel(model="m", api_key="k", base_url="https://example.test")
        _ = await model.response([Message.user("hi")])
        assert created[0].kwargs["base_url"].endswith("/v1")
        await model.aclose()
        assert created[0].closed is True

        embedder = OpenAIEmbedder(model="e", api_key="k", base_url="https://example.test")
        _ = await embedder.embed(["a"])
        assert created[1].kwargs["base_url"].endswith("/v1")
        await embedder.aclose()
        assert created[1].closed is True

    asyncio.run(run())


def test_openai_get_or_create_client_requires_asyncopenai(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(openai_provider.openai, "AsyncOpenAI", None)

    async def run() -> None:
        model = OpenAIChatModel(model="m", api_key="k")
        with pytest.raises(LlmError) as exc:
            await model._get_or_create_client()
        assert exc.value.code == "invalid_request"

        embedder = OpenAIEmbedder(model="e", api_key="k")
        with pytest.raises(LlmError) as exc2:
            await embedder._get_or_create_client()
        assert exc2.value.code == "invalid_request"

    asyncio.run(run())


def test_openai_chat_maps_permission_denied_error() -> None:
    def responses_handler(_kwargs):
        response = httpx.Response(403, request=httpx.Request("POST", "https://example.test"))
        raise openai.PermissionDeniedError("nope", response=response, body=None)

    def embeddings_handler(_kwargs):
        raise AssertionError("not used")

    async def run() -> None:
        client = _FakeOpenAIClient(responses_handler=responses_handler, embeddings_handler=embeddings_handler)
        model = OpenAIChatModel(model="m", api_key="k", client=client)
        with pytest.raises(LlmError) as exc:
            await model.response([Message.user("hi")])
        assert exc.value.code == "auth_error"

    asyncio.run(run())


def test_openai_chat_maps_connection_error() -> None:
    def responses_handler(_kwargs):
        request = httpx.Request("POST", "https://example.test")
        raise openai.APIConnectionError(message="boom", request=request)

    def embeddings_handler(_kwargs):
        raise AssertionError("not used")

    async def run() -> None:
        client = _FakeOpenAIClient(responses_handler=responses_handler, embeddings_handler=embeddings_handler)
        model = OpenAIChatModel(model="m", api_key="k", client=client)
        with pytest.raises(LlmError) as exc:
            await model.response([Message.user("hi")])
        assert exc.value.code == "provider_error"
        assert exc.value.retryable is True

    asyncio.run(run())


def test_openai_chat_maps_bad_request_and_unprocessable_entity() -> None:
    def responses_handler(kwargs):
        response = httpx.Response(400, request=httpx.Request("POST", "https://example.test"))
        if kwargs["input"][0]["content"] == "bad":
            raise openai.BadRequestError("bad", response=response, body=None)
        response2 = httpx.Response(422, request=httpx.Request("POST", "https://example.test"))
        raise openai.UnprocessableEntityError("nope", response=response2, body=None)

    def embeddings_handler(_kwargs):
        raise AssertionError("not used")

    async def run() -> None:
        client = _FakeOpenAIClient(responses_handler=responses_handler, embeddings_handler=embeddings_handler)
        model = OpenAIChatModel(model="m", api_key="k", client=client)
        with pytest.raises(LlmError) as exc:
            await model.response([Message.user("bad")])
        assert exc.value.code == "invalid_request"

        with pytest.raises(LlmError) as exc2:
            await model.response([Message.user("nope")])
        assert exc2.value.code == "invalid_request"

    asyncio.run(run())


def test_openai_chat_maps_api_error_and_fallback() -> None:
    def responses_handler(kwargs):
        if kwargs["input"][0]["content"] == "500":
            response = httpx.Response(500, request=httpx.Request("POST", "https://example.test"))
            raise openai.InternalServerError("err", response=response, body=None)
        if kwargs["input"][0]["content"] == "409":
            response = httpx.Response(409, request=httpx.Request("POST", "https://example.test"))
            raise openai.ConflictError("conflict", response=response, body=None)
        raise ValueError("boom")

    def embeddings_handler(_kwargs):
        raise AssertionError("not used")

    async def run() -> None:
        client = _FakeOpenAIClient(responses_handler=responses_handler, embeddings_handler=embeddings_handler)
        model = OpenAIChatModel(model="m", api_key="k", client=client)

        with pytest.raises(LlmError) as exc:
            await model.response([Message.user("500")])
        assert exc.value.code == "provider_error"
        assert exc.value.retryable is True

        with pytest.raises(LlmError) as exc2:
            await model.response([Message.user("409")])
        assert exc2.value.code == "provider_error"
        assert exc2.value.retryable is False

        with pytest.raises(LlmError) as exc3:
            await model.response([Message.user("fallback")])
        assert exc3.value.code == "provider_error"

    asyncio.run(run())


def test_openai_chat_schema_validation_error() -> None:
    try:
        import jsonschema  # noqa: F401
    except ImportError:
        pytest.skip("jsonschema is not installed")

    def responses_handler(_kwargs):
        return _FakeParsedResponse(output_text="ignored", output_parsed={"a": 1}, id="r-schema")

    def embeddings_handler(_kwargs):
        raise AssertionError("not used")

    schema = {
        "type": "object",
        "properties": {"b": {"type": "string"}},
        "required": ["b"],
        "additionalProperties": False,
    }

    async def run() -> None:
        client = _FakeOpenAIClient(responses_handler=responses_handler, embeddings_handler=embeddings_handler)
        model = OpenAIChatModel(model="m", api_key="k", client=client)
        with pytest.raises(LlmError) as exc:
            await model.response([Message.user("hi")], response_schema=schema)
        assert exc.value.code == "parse_error"

    asyncio.run(run())
