# RAG Trigger Studio

**A local-first desktop workspace for preparing project context for AI-assisted development.**

RAG Trigger Studio helps developers choose which project files to share with a configured AI Core, measure context size, redact common secret-like values, and inspect the operational checks applied before a request is sent.

> **Audit the operation, not the customer's content.**

## What it does

- **Project context:** scan a folder, inspect the project tree, and select the files to include.
- **Secret protection:** redact common passwords, tokens, API keys, and other configured sensitive values.
- **Token accounting:** measure context and instruction tokens against the configured limit.
- **Deterministic Micro-Kernel:** evaluate operational facts independently of AI inference.
- **Local AI Core:** use Ollama or an OpenAI-compatible provider; a deterministic Test Core supports repeatable tests without a model.
- **Developer Diagnostics:** inspect provider/model details, selected-file counts, token metrics, and Kernel availability.
- **Session Feedback and Audit:** explicitly submit tester observations and optionally write operational evidence to `output/context_sync_audit.md`.

The Kernel uses four stages: **OBSERVE → COMPARE → EVALUATE → RESPOND**. Its outcomes are SAFE, WARNING, BLOCKED, or INVALID. It does not call an LLM or access the filesystem or network itself.

## Screenshots

The testing-ground PR will include genuine screenshots captured from the verified application: the project tree and context selection, the Feedback area, Developer Diagnostics, and the resulting audit. Screenshots will reflect the implemented UI rather than mockups.

## Quick start

### 1. Install system dependencies

Ubuntu/Debian:

```sh
sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip libegl1
```

Arch Linux:

```sh
sudo pacman -Syu
sudo pacman -S --needed python python-pip mesa libglvnd
```

The Arch package names and Qt runtime dependencies are distribution-specific. See [docs/INSTALLATION.md](docs/INSTALLATION.md) for troubleshooting and the full tester setup.

### 2. Install Python dependencies

From the repository root:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### 3. Launch the application

```sh
python3 main_ui.py
```

The desktop interface can open without dispatching an AI request. To use AI dispatch, install and start a supported local Core. For Ollama, one example model is `qwen2.5-coder:3b`.

## Feedback and audit behaviour

1. Enter an observation in **Session Feedback** and select **Submit Feedback**.
2. The observation is retained for the current application session and is not added to the AI prompt or project context.
3. Enable **Export Session Verification Audit Trail (.md)** and start a run to create the audit.
4. The audit records operational metrics, Kernel evidence, execution status, and submitted feedback. It is designed not to include the raw prompt or assembled project context.

The audit is local runtime output and is excluded from version control. If an enabled audit cannot be written before execution, the request is not started and the UI reports the failure.

## Testing

Deterministic tests do not require an AI model, API key, or GPU. From the repository root:

```sh
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

For the optional real Ollama integration test, make sure the service and configured model are available, then run:

```sh
RAG_RUN_LOCAL_CORE=1 python -m pytest -q tests/test_local_core.py
```

The Ollama test is opt-in and is separate from the deterministic CI suite.

## Privacy and limitations

- Runtime configuration, generated audits, context snapshots, and other local output are excluded from version control.
- The audit records operational facts rather than the raw prompt or assembled source context. Submitted feedback is intentionally recorded, so do not put secrets or customer content into feedback.
- Redaction is a defensive layer, not a guarantee that every possible secret format will be detected.
- Local-first operation does not itself guarantee that every configured provider or installed service is offline. Verify your Core and network configuration.

## Project documentation

- [Installation and tester preparation](docs/INSTALLATION.md)
- [Testing workflow and controlled QA scenarios](docs/TESTING_WORKFLOW.md)
- [Core testing boundary](CORE_TESTING.md)
- [Issue 5 QA findings](research/experiments/RAG_TRIGGER_STUDIO_2_1_1_QA_FINDINGS.md)

