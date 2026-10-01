# RAG Trigger Studio 2.1.1 — QA Findings and Workbench Evidence

## Purpose

This document records the implementation and manual QA evidence gathered during the 2.1.1 work arising from Issue #5.

The goal is to preserve what was actually observed, including failures encountered during development, rather than replacing the history with only a final-success description.

## Branch and review context

- Repository: StoneVeld-Studios/RAG_Trigger_Studio
- Work branch: `experiment/rag-trigger-2.1.1-core-architecture`
- Pull request: #7 — `2.1.1 Core architecture and two-stage testing`
- Issue origin: #5 — QA Testing / Cross-Platform UI Rendering and Context Loading Verification
- Issue #5 remains open while the 2.1.1 work continues.
- Main was not changed by this work.

## Automated evidence

### Baseline failure

The first local test run after the implementation work could not collect the suite because `main_ui.py` contained malformed audit-log syntax.

That was repaired before continuing.

### Context-selection and Kernel observation test

The new test initially exposed several test-fixture/API mismatches:

1. Qt base initialization was missing in the test fixture.
2. The test expected `KernelResult.observation`, but the actual API exposes `KernelResult.observations`.
3. The returned `observations` value is a dictionary, not an Observation object.
4. The test was corrected to use the actual dictionary structure.

The observed Kernel result was:

- files_discovered: 3
- files_included: 1
- files_excluded: 2
- read_failures: 0
- redaction_count: 1
- token_count: 1
- token_limit: 100

The targeted test subsequently passed:

```
1 passed in 0.12s
```

This is direct evidence that changing the selected context changes the final facts observed by the Kernel, while the Kernel implementation itself remains unchanged.

### Full-suite status

After the final targeted-test correction, the complete deterministic test suite was run again from the repository root.

The resulting local test status was:

* 31 passed
* 1 skipped

The skipped test is the real local Ollama Core integration test. It is intentionally opt-in and requires `RAG_RUN_LOCAL_CORE=1`, because it depends on a locally running Ollama service and model rather than the deterministic repository test environment.

The deterministic Stage 1 suite is therefore green.

The corresponding GitHub Actions run on the current branch also completed successfully, including:

* Python 3.14 environment setup
* Linux Qt/EGL runtime dependency installation
* dependency installation
* application compilation
* complete pytest suite

The real local Ollama integration remains a separate Stage 2 evidence boundary and is not required for the deterministic GitHub Actions suite.


## Manual application QA

The normal application was launched using the documented command:

```
python3 main_ui.py
```

The application was tested interactively rather than through a special test mode.

Observed behaviour:

- RAG Trigger Studio launched successfully.
- The application discovered the Ollama Core.
- The UI reported separately that the Ollama serving engine/model was not currently started.
- The project tree rendered correctly.
- Folder and file selection worked.
- Individual files could be selected and deselected.
- Automatic exclusions were visible in the tree.
- Automatically excluded entries could not be selected.
- Developer Diagnostics expanded correctly.
- Feedback text input worked.
- Instruction-token counting was visible and updated.
- The planned user-facing terminology was present.
- The application remained usable without an Ollama engine being started.

The distinction between Core discovery and an actively serving local engine is intentionally retained. The UI should report what is actually available rather than implying that a model is running when it is not.

## Issue #5 synthetic QA workspace

A synthetic workspace was added at:

`qa/issue-5-workspace/`

It is intended only as reproducible test material. It is not a special execution mode and does not alter normal application behaviour.

It contains:

- ordinary source material
- documentation
- JSONL data
- a synthetic bearer-like value for redaction testing
- automatically excluded directories
- an unsupported binary-like fixture represented as text with a binary extension
- generated/output material

The workspace contains no real customer, account, credential, or personal information.

The normal application successfully loaded this workspace and displayed its material in the project tree.

This gives reviewers and testers a reproducible workspace without requiring anyone to expose private project files or unsanitized JSONL/context data.

## Current architectural evidence

The effective 2.1.1 flow being validated is:

Scanner
→ available project material
→ user selection
→ assembled context
→ final operational facts
→ Kernel
→ Core

The important boundary is that the scanner result is not treated as the final user context.

The user controls the selected material. The final Kernel observation reflects that selected/assembled context.

The intended separation remains:

**Application observes → Kernel evaluates → Diagnostic layer reports**

## Manual UX findings

The following improvements were identified during real use of the application.

### Project tree

The tree is functional and understandable, but the current dark background is visually heavy.

Proposed small UX improvement:

- use a lighter neutral background for the tree
- retain clear selection contrast
- optionally use small standard Qt file/folder icons
- keep the tree simple and terminal-like rather than turning it into a decorative file browser

### Feedback area

The feedback text box works, but entering text currently does not make an obvious acceptance/submission action available.

The desired behaviour is not to create arbitrary files simply because text was entered.

A future small UX change should provide an explicit acknowledgement/acceptance action while preserving the existing session/audit design.

### User instructions

Current heading:

`Enter Promp Instructions or Structural Targets:`

Proposed wording:

**User instruction(s):**

Proposed tooltip:

**Instructions for the local AI. Token usage is counted automatically as you type.**

The wording should remain understandable to non-specialist users. Technical tokenizer details belong in diagnostics rather than the primary user-facing label.

## Planned larger QA fixture

The current synthetic workspace should be expanded into a substantial reviewer/tester scenario.

Planned scenarios:

- QA-01 — full workspace selection
- QA-02 — partial selection and parent tri-state behaviour
- QA-03 — automatic exclusions
- QA-04 — JSONL context loading
- QA-05 — synthetic redaction
- QA-06 — large-context/token accounting
- QA-07 — user-instruction token accounting
- QA-08 — final-context Kernel observation

The larger fixture should remain entirely synthetic and safe to share publicly.

## Evidence policy

Development failures are retained as part of the work history.

The desired evidence chain is:

**failed → investigated → changed → targeted test → full test → manual QA → documented result**

No production behaviour should be changed merely to make a test pass when the evidence shows the test is reading an API incorrectly.

## Remaining work and follow-up

The core 2.1.1 implementation and deterministic test path have now been validated.

Completed evidence includes:

1. The final targeted Kernel observation test was corrected against the actual `KernelResult.observations` API.
2. The complete deterministic local suite passes with 31 tests passing and 1 intentionally skipped Stage 2 integration test.
3. GitHub Actions passes on the current branch, including the Linux Qt/EGL runtime setup.
4. Installation and testing procedures are documented separately in `docs/INSTALLATION.md` and `CORE_TESTING.md`.
5. Manual application QA has been performed and the observed behaviour is recorded above.
6. The branch has been reviewed against the current `main` line, with final reconciliation still pending'

The following items remain as follow-up work rather than unresolved evidence failures:

* Expand the synthetic QA workspace into the planned QA-01 through QA-08 reviewer scenarios.
* Implement the small UX improvements identified during manual use.
* Repeat additional GUI scenarios where useful for future tester coverage.
* Continue improving reviewer/tester documentation as new evidence is gathered.

These follow-up items should not be represented as evidence that the deterministic 2.1.1 test path is failing.

The evidence boundary remains explicit:

**Stage 1:** deterministic repository tests and CI validation.

**Stage 2:** real local Ollama/Core integration, requiring a locally available serving engine and model.

The branch can therefore proceed through the normal review and merge process once the final branch reconciliation and review checks are complete.
