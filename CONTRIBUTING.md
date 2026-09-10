# Contributing to RAG Studio AI Wrapper

Thank you for taking an interest in RAG Studio.

RAG Studio is an open-source, local-first desktop application for preparing,
inspecting, protecting, and delivering project context to a local AI model.

## Before opening an issue: **Please check existing issues and discussions first.**

**For bugs, include:**

- RAG Studio version or commit
- Operating system
- What you were testing
- What you expected
- What actually happened
- Steps to reproduce
- Relevant screenshots or logs with private information removed

Do not upload private source code, credentials, API keys, passwords, SSH keys,
or other sensitive material.

## Testing locally

Create and activate a virtual environment:

    python3 -m venv .venv
    source .venv/bin/activate

Install dependencies:

    python -m pip install -r requirements.txt
    python -m pip install -r requirements-dev.txt

Run tests:

    pytest -q

Compile the main modules:

    python -m py_compile main_ui.py lib/kernel.py

## Pull requests

Please keep pull requests focused on one logical change where practical. Small,
clearly explained changes are easier to review, test, and maintain.

**Before opening a pull request:**

- run the test suite
- run the compile check
- review the Git diff
- avoid committing local environments, generated output, private data, or credentials
- make sure the pull request description explains what changed and why

### Pull request expectations

**When opening a pull request, please describe:**

- what problem the change addresses
- what was changed
- how the change was tested
- any known limitations or remaining concerns

For behaviour changes, include reproducible testing steps where possible. GitHub
Actions automatically runs the project's test workflow for relevant pushes and pull
requests.

A pull request may be reviewed, tested, requested for changes, or declined if it does
not meet the project's requirements. Please do not assume that a passing test suite
means a pull request will be merged. Changes are reviewed for correctness, security,
privacy, maintainability, and consistency with the project's design principles.

Contributors should respond constructively to review comments and update their pull
request when changes are requested.

### Keep changes safe

**Do not include:**

- passwords or API keys
- private keys or credentials
- customer data or private source code
- local `.venv` directories
- generated files that do not belong in the repository
- unrelated formatting or refactoring mixed into an otherwise focused change

When a change affects security, privacy, data handling, or AI/model interaction,
explain the impact clearly in the pull request.

## Community testing

External testing is especially valuable during v2.1 development. Testers are encouraged
to challenge the application claims rather than simply confirm that the application launches.

**Useful feedback includes:**

- unexpected files being included
- expected files being excluded
- filtering behaving unexpectedly
- context calculations appearing incorrect
- file-reading failures
- redaction behaviour
- unclear UI behaviour
- unexpected network or model behaviour

Small, reproducible reports are extremely valuable.
