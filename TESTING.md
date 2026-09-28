# Tester Feedback & Reporting

## Purpose

This guide defines where external testing evidence belongs and how to report it without mixing automated test data, private customer content, and project discussion.

The current external-testing work is tracked through **Issue #5 — [QA Testing] Cross-Platform UI Rendering and Context Loading Verification**.

Issue #5 remains the primary tracking point for the broader QA effort. Individual experiments may address specific questions raised by that issue.

## Before Testing

Use a controlled synthetic fixture whenever possible.

A useful fixture should contain representative cases such as:

- short text;
- source code;
- Unicode text;
- a deliberately long file;
- binary or non-text content.

Do not use customer directories or private source material when a synthetic fixture can reproduce the behaviour.

## What to Record

For a useful reproducible report, capture the information relevant to the observed behaviour.

### Environment

Record, where applicable:

- operating system and version;
- Python version;
- Qt version;
- AI/backend version;
- CPU;
- GPU;
- relevant application commit or release.

### Test Conditions

Record:

- fixture/file-count summary;
- approximate byte-count summary;
- launch timing when relevant;
- indexing/context-loading timing;
- first-query timing when relevant;
- whether the behaviour reproduces after a fresh process;
- whether a repeated run on the same fixture reproduces it.

Do not include unnecessary local paths or private filenames.

## Separate the Problem

When testing context behaviour, distinguish between:

1. **Indexing failure** — the application failed to load or process material that should have entered the context.
2. **Retrieval omission** — material was loaded but was not returned or selected for the relevant operation.
3. **Display truncation** — the underlying context exists but the UI does not display all of it.

When testing UI behaviour, describe the exact visible symptom rather than only reporting that the interface "doesn't work."

## Where Feedback Goes

### General observation, question, or testing discussion

Use the repository's GitHub **Discussions**, when enabled for the repository.

Examples:

- observations that do not yet establish a defect;
- questions about expected behaviour;
- discussion of test methodology;
- cross-platform observations that need investigation.

### Reproducible defect

Use a GitHub **Issue** when the evidence describes a specific reproducible defect.

Include:

- environment;
- relevant commit/release;
- exact reproduction steps;
- expected behaviour;
- actual behaviour;
- relevant redacted logs or excerpts;
- screenshots where useful.

If the defect belongs to the scope of Issue #5, reference **Issue #5** rather than creating an isolated trail with no relationship to the QA effort.

### Feedback on a specific proposed change

Use the relevant **Pull Request conversation/review** when the feedback concerns a specific implementation change.

### Automated reproducible behaviour

Automated tests belong under `tests/`.

Tests should use deterministic synthetic data where practical and should not require private customer material.

### Experiment results

When a test answers a defined research question, record the result in the appropriate experiment record under `research/experiments/`.

An experiment record should state:

- the question;
- the hypothesis;
- the scope;
- what was actually tested;
- the evidence;
- the result;
- known limitations;
- the relationship to the originating Issue or other project requirement.

## Privacy and Diagnostic Data

Do not upload:

- customer source code;
- credentials;
- API keys;
- passwords;
- SSH private keys;
- private directory contents;
- unredacted prompts or retrieved documents;
- raw diagnostic files when they contain local paths or private content.

A redacted excerpt and a stable reproduction procedure are preferable to a raw diagnostic dump.

## Traceability

The preferred evidence chain is:

**Issue → research question → experiment → implementation → automated/manual evidence → result → known limitation → next experiment**

For the current QA work:

**Issue #5**
→ broader cross-platform and context-loading QA requirement

**Kernel Live Observation 001**
→ tests the observation/evidence foundation

**`main_ui.py`**
→ implementation of live scanner observation

**`tests/test_scan_integration.py`**
→ reproducible scanner/kernel evidence

**experiment record**
→ documents exactly what was and was not established

**future QA experiments**
→ address remaining UI, rendering, context, cross-platform, and tester-workflow questions.

The purpose of this structure is not to make every test look successful. It is to make it possible for another person to follow the evidence and determine exactly what has been established and what remains unknown.
