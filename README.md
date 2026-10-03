# RAG Trigger Studio

**2.1.1 architecture work**

RAG Trigger Studio is a local-first desktop application for preparing, inspecting, protecting, and delivering project context
to a local AI model. It is designed around a simple principle:

> **Audit the operation, not the customer's content.**

RAG Trigger Studio helps developers work with large project codebases by providing context collection, token accounting, security redaction,
deterministic safety evaluation, and local model integration.

## What it does

- **Select project context:** scan a project and choose which supported files to include.
- **Protect sensitive values:** detect and redact common secret-like values before context is assembled.
- **Measure context:** track selected files, context tokens, instruction tokens, and the configured limit.
- **Evaluate operational safety:** use a deterministic Micro-Kernel to report SAFE, WARNING, BLOCKED, or INVALID conditions.
- **Connect to a local AI Core:** use Ollama, an OpenAI-compatible provider, or the deterministic Test Core.
- **Inspect and report:** use Developer Diagnostics, submit tester feedback, and optionally export a session audit to `output/context_sync_audit.md`.

The audit records operational facts and explicitly submitted feedback; it is designed not to include the raw prompt or assembled project context. Runtime output is local and excluded from version control.

## Interface and screenshots

Screenshots will be added after the updated feedback and audit workflow has been run and captured from the actual application. They will show the project tree/context selection, Feedback area, Developer Diagnostics, and a representative audit result. No mock interface images are used.

---

## Why RAG Trigger Studio?

Working with AI against a real codebase creates several practical problems:

* Large project context can exceed model limits.
* Project files may contain credentials or sensitive values.
* File-reading failures can result in incomplete context.
* AI pipelines need clear operational boundaries.
* Audit information should not unnecessarily reproduce customer source material.

RAG Trigger Studio is designed to make these conditions visible and controllable.

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
| SAFE      | Valid observation within limits                  | Allowed              |
| WARNING   | Valid observation approaching a configured limit | Allowed with warning |
| BLOCKED   | Unsafe operating condition detected              | Prevented            |
| INVALID   | Observation data is malformed or inconsistent    | Prevented            |

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

RAG Trigger Studio includes a text-based SecurityRedactor. It detects and replaces common sensitive values including:

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

RAG Trigger Studio communicates with an execution Core through an engine-neutral provider boundary. The repository includes a deterministic Test Core for reviewer testing, an Ollama provider, and an OpenAI-compatible provider path. The deterministic Micro-Kernel remains separate from AI inference and evaluates operational conditions independently of the Core.

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

RAG Trigger Studio can scan a selected project directory and assemble context for the AI pipeline. The scanner supports different
file-selection modes and excludes common development directories such as:

* .git
* .venv
* __pycache__
* generated output directories

Context size is measured before dispatch so token pressure can be identified.

---

## Installation

### Requirements

* Python 3
* Python virtual environment support
* PyQt6
* Ollama
* A compatible local AI model

Python dependencies are listed in requirements.txt.

### Create a virtual environment

From the repository root:

python3 -m venv .venv

Activate it:

source .venv/bin/activate

Install application dependencies:

python -m pip install -r requirements.txt

Install test/development dependencies when you intend to run the test suite:

python -m pip install -r requirements-dev.txt

### Linux Qt runtime dependency

PyQt6 is installed through requirements.txt, but Linux also needs the operating-system EGL runtime library used by Qt.

On Debian/Ubuntu:

sudo apt-get update
sudo apt-get install -y libegl1

This is an operating-system dependency, not a Python dependency, so it is intentionally not placed in requirements.txt.

The GitHub Actions workflow installs the same dependency on its Ubuntu runner.

For the complete installation and tester preparation procedure, see docs/INSTALLATION.md.

### Install Ollama

Install Ollama for your operating system using its official documentation. Then install a compatible model, for example:
ollama pull qwen2.5-coder:3b. Make sure Ollama is running before using AI dispatch functionality.

---

## Running RAG Trigger Studio

From the repository directory:

python3 main_ui.py

The application launches as a PyQt6 desktop application.

---

## Testing

RAG Trigger Studio uses a two-stage validation path.

### Stage 1 — deterministic repository test

No AI engine is required. Run from the repository root:

python -m pytest -q

The suite includes a deterministic Test Core and an OpenAI-compatible protocol test using a local synthetic HTTP server. GitHub reviewers can therefore validate the Core architecture without installing a model or connecting to an external service.

### Stage 2 — real local Core

After installing a supported local engine and model, run the optional real-engine test. For Ollama:

RAG_RUN_LOCAL_CORE=1 python -m pytest -q tests/test_local_core.py

The Stage 2 test is intentionally opt-in and is not part of the default GitHub CI run.

See CORE_TESTING.md for the complete testing boundary and provider details, and docs/INSTALLATION.md for the complete tester installation procedure.

---

## Privacy Boundaries

RAG Trigger Studio is designed for local-first operation. The project intentionally separates operational auditing from
customer content. Generated runtime material such as:

* local configuration
* manifests
* generated output
* context snapshots

...is excluded from version control. The repository should contain source code and synthetic test material rather than
private customer or project data.

### Important

Local-first does not automatically mean that every deployment is private. Network configuration, Ollama configuration,
model configuration, operating-system behaviour, and other installed software can affect where data travels. Users remain
responsible for verifying the environment in which they run RAG Trigger Studio.

---

## Repository Structure

RAG_Trigger_Studio/
lib/
kernel.py
redactor.py
token_counter.py
...
tests/
test_kernel.py
test_redactor.py
config/
main_ui.py
requirements.txt
requirements-dev.txt
CORE_TESTING.md
docs/
INSTALLATION.md
LICENSE
README.md

Local runtime directories and configuration files are excluded from version control.
