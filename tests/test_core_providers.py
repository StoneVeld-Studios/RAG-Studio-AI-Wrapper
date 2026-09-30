import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from lib.core import CoreRequest
from lib.core_providers import (
    DummyCoreProvider,
    OpenAICompatibleConfig,
    OpenAICompatibleProvider,
)


def test_dummy_core_is_deterministic_and_requires_no_engine():
    provider = DummyCoreProvider(context_limit=2048)
    request = CoreRequest(context="project context", instructions="inspect this")

    first = provider.generate(request)
    second = provider.generate(request)

    assert first == second
    assert first.provider == "Test Core"
    assert first.model == "deterministic-test"
    assert first.context_limit == 2048
    assert "Context characters: 15" in first.text


def test_dummy_core_rejects_invalid_context_limit():
    with pytest.raises(ValueError):
        DummyCoreProvider(context_limit=0)


def test_openai_compatible_provider_uses_chat_completion_contract():
    received = {}

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            received["path"] = self.path
            length = int(self.headers["Content-Length"])
            received["body"] = json.loads(self.rfile.read(length))
            response = {
                "choices": [
                    {"message": {"content": "real protocol response"}}
                ]
            }
            encoded = json.dumps(response).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

        def log_message(self, *_args):
            pass

    server = HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        provider = OpenAICompatibleProvider(
            OpenAICompatibleConfig(
                base_url=f"http://127.0.0.1:{server.server_port}/v1",
                model="test-model",
                context_limit=8192,
            )
        )

        result = provider.generate(
            CoreRequest(context="assembled context", instructions="test instruction")
        )

        assert result.text == "real protocol response"
        assert result.model == "test-model"
        assert result.context_limit == 8192
        assert received["path"] == "/v1/chat/completions"
        assert received["body"]["model"] == "test-model"
        assert received["body"]["messages"] == [
            {"role": "system", "content": "assembled context"},
            {"role": "user", "content": "test instruction"},
        ]
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_openai_compatible_provider_rejects_malformed_response():
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            body = b'{"unexpected": true}'
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *_args):
            pass

    server = HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        provider = OpenAICompatibleProvider(
            OpenAICompatibleConfig(
                base_url=f"http://127.0.0.1:{server.server_port}",
                model="test-model",
                context_limit=4096,
            )
        )

        with pytest.raises(RuntimeError, match="invalid chat response"):
            provider.generate(CoreRequest(context="", instructions="test"))
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
