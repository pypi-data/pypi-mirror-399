from __future__ import annotations

import json
import re
from typing import Any


def extract_json(text: str) -> Any:
    """Best-effort JSON extraction for LLM responses.

    Supports:
    - raw JSON
    - fenced code blocks (```json ... ```)
    - a JSON value embedded in surrounding text
    """
    raw = text.strip()
    if not raw:
        raise ValueError("Response was empty")

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    for match in re.finditer(r"```(?:json)?\s*(.*?)\s*```", raw, flags=re.DOTALL | re.IGNORECASE):
        candidate = match.group(1).strip()
        if not candidate:
            continue
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            continue

    decoder = json.JSONDecoder()
    for index, ch in enumerate(raw):
        if ch not in "[{":
            continue
        try:
            value, _end = decoder.raw_decode(raw[index:])
            return value
        except json.JSONDecodeError:
            continue

    raise ValueError("Response did not contain valid JSON")

