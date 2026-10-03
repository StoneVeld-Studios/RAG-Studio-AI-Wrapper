# Issue #5 QA Test Workspace

This workspace is the controlled synthetic test ground for RAG Trigger Studio cross-platform QA.

## Purpose

Use this workspace to test context loading, file selection, automatic exclusions, redaction, structured data handling, context-size behaviour, and reproducibility across clean application runs.

The workspace contains no real customer, account, credential, or personal information.

## Two Testing Tracks

### UI / Rendering

Use the workspace while observing:

- project-tree rendering and selection state
- visible text rendering and Unicode handling
- feedback-area behaviour
- diagnostics presentation
- visible errors or lag
- reproducibility after a fresh process

Record the operating system, Python/Qt versions, Core information where relevant, and the exact visible symptom.

### Context Loading

Use the same workspace to compare expected fixture behaviour with application observations.

Pay attention to:

- discovered and selected file counts
- excluded files and directories
- byte-count summaries where available
- token/context counts
- redaction counts
- JSONL handling
- large-context behaviour
- whether a problem is indexing, retrieval, or display truncation

## Fixture Material

The workspace intentionally contains:

- short documentation text
- source code
- Unicode content
- valid JSONL data
- malformed JSONL data
- incomplete JSONL data
- deliberately long text
- synthetic redaction material
- a deliberately non-text/binary-like fixture
- excluded-directory material
- generated-looking output material

Some excluded directories contain small fixture files. Their purpose is to verify that automatic exclusion rules behave consistently.

## Scenario Map

- **QA-01:** Full workspace baseline
- **QA-02:** Partial selection and tri-state behaviour
- **QA-03:** Automatic exclusions
- **QA-04:** JSONL context loading, including malformed and incomplete cases
- **QA-05:** Synthetic redaction
- **QA-06:** Large context and token-limit accounting
- **QA-07:** User-instruction token accounting
- **QA-08:** Final-context Kernel observation

Scenario definitions and completion status are maintained as part of the testing workflow. The presence of fixture files does not mean that a scenario has already passed.

## Safe Reporting

A tester may use this workspace to produce reproducible evidence without exposing their own project files.

Useful evidence includes:

- operating system and Python version
- Qt/PyQt version
- CPU/GPU information where useful
- application behaviour and visible errors
- file-count and byte-count summaries
- token/context counts
- timings
- Kernel state
- diagnostic output that contains only synthetic material
- a concise description of what was observed

Do not add personal or customer data to this workspace before sharing it.

Do not paste raw diagnostics, JSONL, prompts, or context contents into GitHub if they may contain private data. Prefer a redacted excerpt and exact reproduction steps.

## Expected Outcome

A useful result should allow another person to determine:

1. what scenario was run;
2. what was expected;
3. what actually happened;
4. whether the result reproduced;
5. what evidence supports the observation;
6. whether the issue appears deterministic, environment-specific, Core-specific, or display-only.

This workspace is test input. Runtime audit evidence belongs in the application's `output/` directory, not in this fixture.
