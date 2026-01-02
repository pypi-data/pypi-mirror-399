# ARP LLM (`arp-llm`)

Shared helper for calling LLM providers across the ARP/JARVIS stack.

This package provides:
- `ChatModel.response(...)` (chat/text + optional JSON Schema structured output)
- `Embedder.embed(...)` (embeddings)
- `load_chat_model_from_env(...)` / `load_embedder_from_env(...)` profile-based configuration

## Install

```bash
pip install arp-llm
```

## Quickstart (dev mock; no network)

```python
import asyncio

from arp_llm import Message, load_chat_model_from_env_or_dev_mock

async def main() -> None:
    model = load_chat_model_from_env_or_dev_mock()
    resp = await model.response([Message.user("hello")])
    print(resp.text)

asyncio.run(main())
```

## Configuration (OpenAI)

```bash
export ARP_LLM_PROFILE=openai
export ARP_LLM_API_KEY=...
export ARP_LLM_CHAT_MODEL=gpt-4.1-mini
export ARP_LLM_BASE_URL=https://api.openai.com
```

## API

- `ChatModel.response(messages, *, response_schema=None, temperature=None, timeout_seconds=None, metadata=None) -> Response`
  - If `response_schema` is provided, `Response.parsed` will be a JSON-like `dict`.
- `Embedder.embed(texts, *, timeout_seconds=None, metadata=None) -> EmbeddingResponse`

## Direct construction (advanced)

The `load_*_from_env*()` helpers are optional. For multi-provider routing/fallback inside a single process, construct provider clients directly (and route per call), for example:

```python
from arp_llm.providers.openai import OpenAIChatModel

model = OpenAIChatModel(model="gpt-4.1-mini", api_key="...", base_url="https://api.openai.com")
```

See `Business_Docs/JARVIS/LLMProvider/HLD.md` and `Business_Docs/JARVIS/LLMProvider/LLD.md` for the design intent.
