"""Tests for excel_engine.llm.client that never touch the network."""

import pytest

from excel_engine.exceptions.errors import ProductConfigurationError
from excel_engine.llm.client import DEFAULT_MODEL, _get_api_key, _get_model, get_workbook_spec


def test_get_api_key_requires_openai_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ProductConfigurationError, match="OPENAI_API_KEY"):
        _get_api_key()


def test_get_api_key_returns_key_when_set(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")
    assert _get_api_key() == "test-key-123"


def test_get_model_resolves_priority(monkeypatch):
    monkeypatch.delenv("EXCEL_ENGINE_LLM_MODEL", raising=False)
    assert _get_model() == DEFAULT_MODEL

    monkeypatch.setenv("EXCEL_ENGINE_LLM_MODEL", "gpt-4o")
    assert _get_model() == "gpt-4o"

    assert _get_model("custom-model") == "custom-model"


def test_get_workbook_spec_validates_prompt():
    with pytest.raises(ProductConfigurationError, match="cannot be empty"):
        get_workbook_spec("")

    with pytest.raises(ProductConfigurationError, match="cannot be empty"):
        get_workbook_spec("   ")
