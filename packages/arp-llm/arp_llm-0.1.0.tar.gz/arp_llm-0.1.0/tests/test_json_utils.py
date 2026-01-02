import pytest

from arp_llm.json_utils import extract_json


def test_extract_json_empty_raises() -> None:
    with pytest.raises(ValueError):
        extract_json("   ")


def test_extract_json_skips_empty_fence_then_parses() -> None:
    text = "```json\n\n```\n```json\n{\"a\": 1}\n```"
    assert extract_json(text) == {"a": 1}


def test_extract_json_parses_embedded_object() -> None:
    text = "prefix {bad} {\"a\": 1} suffix"
    assert extract_json(text) == {"a": 1}


def test_extract_json_skips_invalid_fenced_block_then_parses() -> None:
    text = "```json\n{bad}\n```\n```json\n{\"a\": 1}\n```"
    assert extract_json(text) == {"a": 1}


def test_extract_json_raises_when_no_json_present() -> None:
    with pytest.raises(ValueError):
        extract_json("no json here")
