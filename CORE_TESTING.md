# Core Testing

RAG Trigger Studio uses a two-stage Core validation path so reviewers do not need to install an AI engine just to test the application architecture.

## Stage 1: deterministic repository test

The normal GitHub test suite runs without Ollama, LM Studio, llama.cpp, a model download, an API key, or GPU hardware.

The test suite includes a deterministic **Test Core** provider. It implements the same Core contract used by real providers and returns a reproducible response.

Run locally from the repository root with:

python -m pytest -q

This is the first validation stage for reviewers.

It verifies the Core boundary, deterministic behaviour, request construction, response handling, and OpenAI-compatible protocol shape without depending on an external AI service.

### Linux Qt runtime dependency

The Python dependency list installs PyQt6 itself, but PyQt6 also relies on operating-system graphics libraries.

For Debian/Ubuntu Linux, install the EGL runtime library before running the test suite:

sudo apt-get update
sudo apt-get install -y libegl1

This dependency is deliberately installed by the GitHub Actions workflow as well. It is an operating-system package, not a Python package, so it does not belong in requirements.txt.

## Stage 2: real local Core

After installing a supported local engine and model, reviewers can run the optional real-engine integration test.

For Ollama, make sure the service is running and the selected model is already available. Then run from the repository root:

RAG_RUN_LOCAL_CORE=1 python -m pytest -q tests/test_local_core.py

The default connection is:

http://127.0.0.1:11434

The default model is:

qwen2.5-coder:3b

A different local endpoint or model can be supplied with RAG_CORE_OLLAMA_HOST and RAG_CORE_OLLAMA_MODEL.

The real test is intentionally opt-in. GitHub CI does not require a user's local engine.

## Provider architecture

The application communicates with a Core contract.

Current providers:

* **Test Core** — deterministic and always available to repository tests.
* **Ollama Core** — native Ollama API integration.
* **OpenAI-compatible Core** — generic /chat/completions integration for compatible services.

The OpenAI-compatible boundary is intended to support services such as LM Studio and llama.cpp server without making their presence a requirement for the base test suite.

A provider name, model name, endpoint, and actual context capacity remain implementation/diagnostic facts. Normal product UI should use engine-neutral wording such as **Core Connected**.

## Evidence boundary

The deterministic test proves that RAG Trigger Studio's own architecture behaves correctly.

The real local test proves that a particular installed Core can actually communicate with the application.

These are separate pieces of evidence and should not be presented as equivalent.
