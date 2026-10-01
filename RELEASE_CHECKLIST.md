# RAG Studio v2.1.0 Tester-Ready Checklist

Use this checklist before inviting external testers or reviewers to evaluate
the public v2.1.0 release.

## Maintainer release gates

- [x] `v2.1.0` tag exists.
- [x] `main` is synchronized with GitHub.
- [x] GitHub Actions test workflow is enabled.
- [x] Automated test suite passes locally.
- [x] CI test workflow passes on `main`.
- [x] Application modules compile with `py_compile`.
- [x] Runtime output, local configuration, manifests, and virtual environments
      are excluded from version control.
- [x] Contributor guidance explains how to remove private data from reports.
- [x] A structured bug-report issue template is available for testers.
- [x] Create a GitHub Release for `v2.1.0` with installation and testing notes.
- [x] Confirm the release notes state whether Ollama is required for basic UI
      testing or only for AI dispatch testing.

## Tester setup

Testers should use a clean clone and a fresh virtual environment:

```bash
git clone https://github.com/StoneVeld-Studios/RAG-Studio-AI-Wrapper.git
cd RAG-Studio-AI-Wrapper
git checkout v2.1.0
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
```

## Automated checks

Run the deterministic test and compile checks:

```bash
pytest -q
python -m py_compile main_ui.py lib/kernel.py
```

Expected result for the current v2.1.0 baseline:

```text
24 passed
```

## Application smoke test

- [ ] Start the application with `python3 main_ui.py` in a graphical session.
- [ ] Confirm the PyQt6 window opens without a traceback. This still requires
      a manual graphical-session check.
- [ ] Select a small synthetic or disposable test project.
- [ ] Confirm the project scan completes.
- [ ] Confirm included and excluded files are visibly distinguishable.
- [ ] Confirm generated output is not written into the repository source tree.
- [ ] Confirm the application remains usable when a file cannot be read.
- [ ] Confirm a context package can be prepared without adding private files
      to the Git repository.

## Deterministic kernel checks

- [ ] Confirm valid observations produce the expected `SAFE` result.
- [ ] Confirm near-limit observations produce `WARNING`.
- [ ] Confirm unsafe observations produce `BLOCKED`.
- [ ] Confirm malformed observations produce `INVALID`.
- [ ] Confirm repeated identical observations produce identical decisions.

## Security and privacy checks

- [ ] Use synthetic credentials only, never real secrets.
- [ ] Confirm common password, token, API-key, and private-key patterns are
      redacted in generated context.
- [ ] Confirm the redaction count is reported without exposing the original
      value.
- [ ] Confirm files outside the selected project are not collected.
- [ ] Confirm `.git`, `.venv`, `__pycache__`, and generated output are excluded.
- [ ] Confirm testers understand that local-first does not guarantee that
      every installed model, service, or network configuration is private.
- [ ] Remove all test secrets, snapshots, and generated context before
      reporting or publishing results.

## Optional Ollama checks

These checks require a working local Ollama installation and a compatible
model. They are separate from the deterministic kernel checks.

- [ ] Confirm Ollama is running locally.
- [ ] Confirm the configured model is available.
- [ ] Confirm AI dispatch reports connection or model errors clearly.
- [ ] Confirm the dispatched context contains only the selected and sanitized
      files.
- [ ] Confirm no unexpected remote service is contacted during the test.

## Bug report format

Every tester report should include:

1. Version or commit tested
2. Operating system and Python version
3. Whether Ollama was enabled
4. Exact command used
5. Expected behavior
6. Actual behavior
7. Minimal reproduction steps
8. Sanitized logs or screenshots
9. Whether the issue is reproducible

Do not attach customer source code, credentials, API keys, passwords, private
keys, or unsanitized context output.

## Clean-clone verification

- [x] A clean clone of the `v2.1.0` tag passed the automated test suite.
- [x] A clean clone of the `v2.1.0` tag passed the compile check.

## Release decision

Publish the release for broader testing only when:

- automated tests and compilation pass;
- the application smoke test passes;
- privacy and redaction checks pass;
- known limitations are written in the release notes; and
- at least one reviewer has reproduced the setup from a clean clone.
