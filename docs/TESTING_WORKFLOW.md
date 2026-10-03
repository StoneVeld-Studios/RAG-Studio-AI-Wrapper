# Testing Workflow

## Purpose

RAG Trigger Studio uses a deterministic, evidence-first testing workflow so that architectural behaviour can be verified without requiring a real AI Core, while real local Core testing remains a separate integration layer.

This document defines the testing ground introduced from the lessons of Issue #5 and the limitations of the earlier JSONL-focused testing proposal in Issue #6.

The objective is not to collect customer content. The objective is to verify that the application handles controlled inputs correctly, records useful operational evidence, and gives reviewers a reproducible way to distinguish defects.

## Testing Model

Testing is divided into four layers:

1. **Deterministic automated tests** verify application and architectural contracts without an external AI service.
2. **Controlled QA fixtures** provide known, synthetic inputs that can be reused across machines and test runs.
3. **Runtime audit evidence** records what operation occurred and what the tester observed without unnecessarily recording customer content.
4. **Human review** uses GitHub issues and pull requests to discuss findings, changes, evidence, and remaining work.

The layers have different responsibilities and should not be mixed.

## Repository Boundaries

### `tests/`

Automated pytest tests belong here.

Tests should verify behaviour and contracts rather than depend on a particular developer machine or private project.

### `qa/`

The `qa/` directory contains controlled, versioned test material.

It is the test ground supplied to reviewers. Files placed here should be synthetic and intentionally designed to exercise specific application behaviour.

Examples include:

- short text
- source code
- Unicode text
- JSON and JSONL
- deliberately large text
- synthetic redaction material
- unsupported or binary-like files
- automatically excluded directories
- generated-looking files used to verify exclusion behaviour

The QA fixture must not contain real customer, credential, account, or personal information.

### `output/`

The application's runtime-generated evidence belongs here.

For example:

- `output/context_sync_audit.md`

Runtime output is evidence produced by an execution. It is not a fixture and should not be treated as controlled QA input.

Runtime output containing local paths, private content, credentials, prompts, or other sensitive material must not be committed to the repository.

### GitHub Issues and Pull Requests

Issues describe requirements, observations, or unresolved work.

Pull requests provide the implementation and its review trail.

A test result should remain traceable to the fixture, scenario, implementation change, and evidence used to establish the result.

## Issue #5 Lessons

Issue #5 requested cross-platform UI rendering and context-loading verification.

Reviewer feedback identified two distinct testing tracks:

### UI / Rendering

Record:

- operating system
- Python version
- Qt/PyQt version
- Core/backend information where relevant
- CPU/GPU information where useful
- exact visible symptom
- whether the symptom reproduces after a fresh process
- whether the behaviour is reproducible on repeated runs

### Context Loading

Record:

- fixture/scenario used
- file-count and byte-count summaries
- indexing or loading timing where useful
- expected chunk/context measurements
- reported context measurements
- observed token counts
- whether the problem is an indexing failure, retrieval omission, or display truncation

The same controlled fixture should be usable for both tracks so that machine-specific setup can be distinguished from deterministic application behaviour.

## Privacy and Evidence

The testing workflow is designed around the principle:

> Audit the operation, not the customer's content.

Reviewers should prefer:

- synthetic fixtures
- counts
- timings
- states
- error descriptions
- redaction counts
- reproducible steps
- redacted diagnostic excerpts

Reviewers should avoid submitting:

- real project directories
- customer files
- credentials
- API keys
- personal information
- unnecessary absolute paths
- raw context contents
- raw JSONL or diagnostic output when it may contain private material

A useful test result explains what happened without requiring disclosure of the material being processed.

## QA Scenarios

The controlled testing ground will grow around explicit scenarios rather than an unstructured collection of files.

Initial scenario families are:

- **QA-01 — Full workspace:** load the complete synthetic workspace and establish baseline counts.
- **QA-02 — Partial selection:** verify selected, excluded, and tri-state directory behaviour.
- **QA-03 — Automatic exclusions:** verify that known excluded directories and generated material are not treated as normal context.
- **QA-04 — JSONL context loading:** exercise valid and malformed structured-line data and verify deterministic handling.
- **QA-05 — Synthetic redaction:** verify that known synthetic secret-like material is redacted and counted without exposing the original value in audit evidence.
- **QA-06 — Large context:** exercise deliberate context growth and token-limit accounting.
- **QA-07 — User instructions:** verify instruction-token accounting independently from loaded context.
- **QA-08 — Final-context Kernel observation:** verify that the final context observation reaches the deterministic Kernel correctly and produces the expected state.

These scenarios are a testing plan, not claims that every scenario is already complete. Each scenario must be implemented and evidenced before being marked complete.

## Feedback and Audit

The Session Feedback area and the session audit are part of the same evidence path.

A reviewer should be able to:

1. perform a controlled test;
2. enter an observation in the Feedback area;
3. explicitly submit that feedback;
4. receive clear UI acknowledgement;
5. generate or complete the session audit;
6. find the submitted observation in `output/context_sync_audit.md`;
7. verify that the audit contains operational evidence rather than customer content.

Feedback is tester evidence. It must not silently become AI context merely because it was entered into the UI.

The audit writer must fail visibly when it cannot produce the requested evidence. Silent exception swallowing is not acceptable for an evidence-producing path.

## Determinism and Repetition

A useful QA result should distinguish:

- a deterministic application defect;
- a machine-specific environment problem;
- an external Core/integration problem;
- a rendering-only problem;
- a data-selection or indexing problem;
- a retrieval problem;
- a display-only truncation problem.

Where practical, reviewers should run the same scenario twice from a clean process.

Differences between the runs are evidence in their own right and should be recorded.

## Relationship to Issue #6

Issue #6 was opened to expand pytest coverage around a proposed JSONL logging layer, especially corrupted, incomplete, and malformed JSONL structures.

The current architecture no longer treats a JSONL logging layer as the primary testing boundary.

The useful requirement from Issue #6 — deterministic handling and testing of malformed or incomplete structured data — remains relevant and is incorporated into the broader QA and automated-testing model.

Issue #6 is therefore considered **superseded in scope, but not yet closed**.

It should remain open until the replacement testing ground and audit/feedback work have been implemented, reviewed, and verified. Once the replacement work is accepted, Issue #6 can be closed with a reference to the resulting PR and this document.

## Workflow for New Testing Work

The project follows this sequence:

1. Research the reported behaviour or requirement.
2. Separate the testing concern into a precise scenario.
3. Define the expected evidence.
4. Update the controlled QA fixture or automated test where necessary.
5. Implement the smallest appropriate application change.
6. Test the changed behaviour directly.
7. Run the complete deterministic suite.
8. Perform relevant manual GUI/Core testing.
9. Review the audit and feedback evidence.
10. Document failures, corrections, and remaining limitations.
11. Open or update the pull request with the complete evidence trail.
12. Only then close or supersede the corresponding issue.

This keeps the test environment, implementation, and evidence aligned.

## Completion Standard

Testing work is not complete merely because the application launches or pytest passes.

A testing-ground change is complete when:

- the intended behaviour is implemented;
- automated tests cover the important contract;
- the controlled QA fixture can reproduce the relevant scenario;
- the UI gives the tester a clear workflow;
- runtime audit evidence is produced correctly;
- privacy boundaries are respected;
- manual evidence has been reviewed where applicable;
- failures are either corrected or explicitly documented;
- the resulting PR provides a clear change and evidence trail.

The purpose of this workflow is reproducibility, transparency, and useful evidence for both maintainers and external reviewers.