"""Core providers used by RAG Trigger Studio.

DummyCoreProvider is deterministic and requires no AI engine.
OpenAICompatibleProvider is the shared boundary for services exposing
the OpenAI-compatible HTTP API shape. Ollama remains a separate provider
because its native API is different.
"""

import json
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .core import CoreRequest, CoreResponse


class DummyCoreProvider:
    """Deterministic provider for repository and reviewer testing."""

    provider_name = "Test Core"

    def __init__(self, context_limit: int = 4096):
        if context_limit <= 0:
            raise ValueError("context_limit must be positive")
        self._context_limit = context_limit

    def context_limit(self) -> int:
        return self._context_limit

    def generate(self, request: CoreRequest) -> CoreResponse:
        return CoreResponse(
            text=(
                "Deterministic test response. "
                f"Context characters: {len(request.context)}. "
                f"Instruction characters: {len(request.instructions)}."
            ),
            provider=self.provider_name,
            model="deterministic-test",
            context_limit=self._context_limit,
        )


@dataclass(frozen=True)
class OpenAICompatibleConfig:
    base_url: str
    model: str
    context_limit: int
    timeout: float = 30.0


class OllamaCoreProvider:
    """Core provider for Ollama's native generate API."""

    provider_name = "Ollama Core"

    def __init__(
        self,
        host: str = "http://127.0.0.1:11434",
        model: str = "qwen2.5-coder:3b",
        context_limit: int = 4096,
        timeout: float = 60.0,
    ):
        if context_limit <= 0:
            raise ValueError("context_limit must be positive")
        self.host = host.rstrip("/")
        self.model = model
        self._context_limit = context_limit
        self.timeout = timeout

    def context_limit(self) -> int:
        return self._context_limit

    def generate(self, request: CoreRequest) -> CoreResponse:
        payload = {
            "model": self.model,
            "prompt": request.context + "\n\n" + request.instructions,
            "stream": False,
            "options": {"num_ctx": self._context_limit},
        }
        http_request = Request(
            self.host + "/api/generate",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urlopen(http_request, timeout=self.timeout) as response:
                result = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError) as exc:
            raise RuntimeError(f"Core request failed: {exc}") from exc

        try:
            text = result["response"]
        except (KeyError, TypeError) as exc:
            raise RuntimeError("Core returned an invalid generation response") from exc

        return CoreResponse(
            text=text,
            provider=self.provider_name,
            model=self.model,
            context_limit=self._context_limit,
        )


class OpenAICompatibleProvider:
    """Provider for engines exposing an OpenAI-compatible chat endpoint."""

    provider_name = "OpenAI-compatible Core"

    def __init__(self, config: OpenAICompatibleConfig):
        if config.context_limit <= 0:
            raise ValueError("context_limit must be positive")
        self.config = config

    def context_limit(self) -> int:
        return self.config.context_limit

    def generate(self, request: CoreRequest) -> CoreResponse:
        payload = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": request.context},
                {"role": "user", "content": request.instructions},
            ],
        }
        url = self.config.base_url.rstrip("/") + "/chat/completions"
        body = json.dumps(payload).encode("utf-8")
        http_request = Request(
            url,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urlopen(http_request, timeout=self.config.timeout) as response:
                result = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError) as exc:
            raise RuntimeError(f"Core request failed: {exc}") from exc

        try:
            text = result["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError("Core returned an invalid chat response") from exc

        return CoreResponse(
            text=text,
            provider=self.provider_name,
            model=self.config.model,
            context_limit=self.config.context_limit,
        )
