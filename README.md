# RAG Studio AI Wrapper

**Version 2.1.0**

RAG Studio AI Wrapper is a local-first desktop application for preparing, inspecting, protecting, and delivering project context
to a local AI model. It is designed around a simple principle:

> **Audit the operation, not the customer's content.**

RAG Studio helps developers work with large project codebases by providing context collection, token accounting, security redaction,
deterministic safety evaluation, and local model integration.

---

## Why RAG Studio?

Working with AI against a real codebase creates several practical problems:

* Large project context can exceed model limits.
* Project files may contain credentials or sensitive values.
* File-reading failures can result in incomplete context.
* AI pipelines need clear operational boundaries.
* Audit information should not unnecessarily reproduce customer source material.

RAG Studio is designed to make these conditions visible and controllable.

---

## v2.1.0 Highlights

Version 2.1 introduces a deterministic Micro-Kernel and strengthened security handling.

### Deterministic Micro-Kernel

The Micro-Kernel follows four stages:

**OBSERVE -> COMPARE -> EVALUATE -> RESPOND**

The kernel:

* does not use an LLM
* does not access the filesystem
* does not access the network
* does not depend on the GUI
* maintains no hidden runtime state
* produces deterministic results

Given the same observation, the kernel produces the same decision.

### Kernel States

| State     | Meaning                                          | Result               |
| --------- | ------------------------------------------------ | -------------------- |
| `SAFE`    | Valid observation within limits                  | Allowed              |
| `WARNING` | Valid observation approaching a configured limit | Allowed with warning |
| `BLOCKED` | Unsafe operating condition detected              | Prevented            |
| `INVALID` | Observation data is malformed or inconsistent    | Prevented            |

The kernel evaluates operational facts including:

* discovered files
* included files
* excluded files
* file-read failures
* redaction count
* token count
* token limit

The kernel is deliberately small and independent of AI inference.

---

## Security Redaction

RAG Studio includes a text-based `SecurityRedactor`. It detects and replaces common sensitive values including:

* passwords
* secrets
* API keys
* authentication tokens
* bearer tokens
* database passwords
* AWS secret assignments
* SSH private keys
* user-specified private targets

The redactor returns:

1. sanitized text
2. the number of redactions performed

This allows the application to track redaction activity without requiring protected values to appear in audit information.

### Security Note

Redaction is a defensive mechanism, not a guarantee that every possible secret format will be detected. Users should still
review their environment and project configuration before processing sensitive material.

---

## Local AI Integration

RAG Studio can communicate with a locally running Ollama service. The development workflow supports local coding models,
for example: `qwen2.5-coder:3b`. The AI model is separate from the deterministic Micro-Kernel. The kernel evaluates operational conditions independently of the model.

---

## Architecture

At a high level:

**Project Files**
**File Scanner**
**Security Redactor**
**Token Counter**
**Deterministic Micro-Kernel**
**Decision**
**Local AI Pipeline**

The kernel does not need to understand the customer's source code. It evaluates the operation using structured observations
supplied by the application.

---

## Context Handling

RAG Studio currently uses whole-directory context assembly rather than conventional retrieval or chunk-based RAG. The scanner
collects the selected files into a single assembled context, which is then measured before dispatch.

The scanner supports different file-selection modes and excludes common development directories such as:

* `.git`
* `.venv`
* `__pycache__`
* generated output directories

Context size is measured before dispatch so token pressure can be identified. The application does not silently truncate the
assembled context; if the final payload exceeds the active context limit, dispatch is blocked.

---

## Installation

### Requirements

* Python 3
* Python virtual environment support
* PyQt6
* Ollama
* A compatible local AI model

Python dependencies are listed in `requirements.txt`.

On Linux, PyQt6 may also require system GUI runtime libraries that are not installed by pip. On Ubuntu/Debian systems, install
the EGL runtime package `libegl1` if it is missing. Other Linux distributions may provide the equivalent package under a different name.


### Create a virtual environment

From the project directory:

`python3 -m venv .venv`

Activate it:

`source .venv/bin/activate`

Install dependencies:

`pip install -r requirements.txt`


### Install Ollama

Install Ollama for your operating system using its official documentation. Then install a compatible model, for example:
`ollama pull qwen2.5-coder:3b`. Make sure Ollama is running before using AI dispatch functionality.

---

## Running RAG Studio

From the repository directory: `python3 main_ui.py`. The application launches as a PyQt6 desktop application.

---

## Testing

RAG Studio includes automated tests covering the deterministic kernel, security redaction, live scanner-to-kernel integration,
and context-assembly continuity.

Run:

`python -m pytest -q`

The current automated suite contains 26 tests. The tests use controlled synthetic data and verify deterministic behaviour,
validation and blocking conditions, redaction behaviour, scanner observations, and preservation of included/excluded content.

For the external testing workflow, see `TESTING.md`. The current external QA work is tracked through GitHub Issue #5.
General testing discussion can use GitHub Discussions; reproducible defects should be reported as GitHub Issues, with Issue #5
referenced where relevant. Experiment results are recorded under `research/experiments/`.

---

## Privacy Boundaries

RAG Studio is designed for local-first operation. The project intentionally separates operational auditing from
customer content. Generated runtime material such as:

* local configuration
* manifests
* generated output
* context snapshots

...is excluded from version control. The repository should contain source code and synthetic test material rather than
private customer or project data.

### Important

Local-first does not automatically mean that every deployment is private. Network configuration, Ollama configuration,
model configuration, operating-system behaviour, and other installed software can affect where data travels.Users remain
responsible for verifying the environment in which they run RAG Studio.

---

## Repository Structure

RAG-Studio-AI-Wrapper/
* `.github/workflows/` — automated GitHub Actions tests
* `config/` — application settings
* `lib/` — kernel, redaction, token, and supporting components
* `research/experiments/` — durable experiment records
* `tests/` — automated tests and controlled synthetic fixtures
* `TESTING.md` — external testing and reporting workflow
* `main_ui.py` — desktop application
* `requirements.txt` — Python runtime dependencies
* `requirements-dev.txt` — development/test dependencies
* `LICENSE`
* `README.md`

Local runtime directories and configuration files are excluded from version control.
