import os

import pytest

from lib.core import CoreRequest
from lib.core_providers import OllamaCoreProvider


@pytest.mark.skipif(
    os.environ.get("RAG_RUN_LOCAL_CORE") != "1",
    reason="Set RAG_RUN_LOCAL_CORE=1 to run the real local Core integration test",
)
def test_local_ollama_core_round_trip():
    host = os.environ.get("RAG_CORE_OLLAMA_HOST", "http://127.0.0.1:11434")
    model = os.environ.get("RAG_CORE_OLLAMA_MODEL", "qwen2.5-coder:3b")

    provider = OllamaCoreProvider(host=host, model=model)
    result = provider.generate(
        CoreRequest(
            context="This is a synthetic GitHub reviewer test context.",
            instructions="Reply with the exact word CORE_OK.",
        )
    )

    assert result.provider == "Ollama Core"
    assert result.model == model
    assert result.text.strip()
