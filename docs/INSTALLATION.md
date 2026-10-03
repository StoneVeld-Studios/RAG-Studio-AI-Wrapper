# RAG Trigger Studio Installation and Test Preparation

This document is the canonical installation path for reviewers and testers.

The goal is to make the environment requirements explicit so that a tester can reproduce the repository tests without relying on the developer's local machine.

## 1. Supported test environment

The repository test workflow currently uses:

* GitHub Actions
* ubuntu-latest
* Python 3.14
* PyQt6 6.11.0
* PyQt6-Qt6 6.11.2
* pytest from requirements-dev.txt

GitHub-hosted runners are fresh virtual machines for each job. System packages required by the application therefore have to be installed by the workflow itself rather than assumed to exist on the runner.

## 2. Python dependencies

From the repository root:

python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt

requirements.txt contains the application/runtime Python dependencies, including the pinned PyQt6 packages.

requirements-dev.txt contains the test-only Python dependencies.

Do not install only requirements.txt when you intend to run the test suite; pytest is intentionally kept in the development/test dependency file.

## 3. Linux Qt runtime dependency

PyQt6 is a Python package, but the Qt GUI stack also requires operating-system libraries.

For Debian/Ubuntu systems, install the EGL runtime library:

sudo apt-get update
sudo apt-get install -y libegl1

The GitHub Actions workflow performs the same installation before importing the PyQt6 application.

On Arch Linux, install Python/pip and the Qt graphics runtime libraries:

sudo pacman -Syu
sudo pacman -S --needed python python-pip mesa libglvnd

Then install the project's Python dependencies in the virtual environment using the commands in Section 2. The Arch package names and dependency details are distribution-specific; if Qt reports a missing shared library, resolve that system dependency with pacman rather than adding an operating-system library to requirements.txt.

These are operating-system dependencies, not Python dependencies, so they are intentionally not placed in requirements.txt. Other Linux distributions may provide the relevant EGL/Qt runtime through differently named packages.

## 4. Running the application

From the repository root with the virtual environment active:

python3 main_ui.py

The application is a PyQt6 desktop application.

## 5. Stage 1 repository test

The deterministic repository test does not require Ollama, a model, an API key, or a GPU.

Run from the repository root:

python -m pytest -q

Use the repository root as the working directory. Do not run the command from inside tests/, because the project imports its top-level lib/ package.

The Qt integration test configures Qt for an offscreen test environment, so the deterministic suite does not require a physical desktop display on CI.

## 6. Stage 2 real Ollama test

Install Ollama separately and make sure the selected model is available.

The default test configuration is:

* Host: http://127.0.0.1:11434
* Model: qwen2.5-coder:3b

Run the explicit integration test from the repository root:

RAG_RUN_LOCAL_CORE=1 python -m pytest -q tests/test_local_core.py

This test is intentionally not part of the default GitHub CI run because GitHub's hosted runner does not contain the developer's local Ollama service or model.

## 7. Test evidence

Keep the two evidence classes separate:

* **Stage 1 / CI evidence:** repository code, deterministic Core behaviour, protocol handling, and application tests.
* **Stage 2 / local evidence:** communication with the specific Ollama installation and model available on the tester's machine.

A successful Stage 1 test does not prove that a particular local AI engine is installed or reachable.

A successful Stage 2 test does not replace the deterministic repository suite.

## 8. Troubleshooting

### ModuleNotFoundError: No module named 'lib'

Check that:

1. the virtual environment is active;
2. the repository dependencies are installed;
3. the command is being run from the repository root; and
4. the command is python -m pytest ...

### ImportError: libEGL.so.1: cannot open shared object file

On Debian/Ubuntu, install the EGL runtime package:

sudo apt-get update
sudo apt-get install -y libegl1

Then rerun the test from the repository root.

### Ollama integration test is skipped

The Stage 2 test is intentionally opt-in. Set RAG_RUN_LOCAL_CORE=1 when you want to perform the real local Core test.

## 9. Files involved in the test environment

* requirements.txt — application Python dependencies.
* requirements-dev.txt — test/development Python dependencies.
* .github/workflows/tests.yml — reproducible GitHub-hosted CI environment and test commands.
* CORE_TESTING.md — Core validation boundary and evidence model.
* tests/ — deterministic and optional integration tests.
