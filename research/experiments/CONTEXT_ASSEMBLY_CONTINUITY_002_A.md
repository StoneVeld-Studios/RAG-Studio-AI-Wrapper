# Context Assembly Continuity 002-A

## Status

Completed implementation and automated evidence for the stated context-assembly boundary.

## Origin and Tracking

This experiment is part of the broader external-testing work tracked by **Issue #5 — [QA Testing] Cross-Platform UI Rendering and Context Loading Verification**.

Experiment 001 established that the existing deterministic kernel can observe facts produced by the real scanner. Experiment 002-A moves one boundary forward: whether content reported as included by the scanner remains identifiable and intact in the assembled context produced by that scanner.

Issue #5 remains open. This experiment does **not** claim to complete cross-platform UI, rendering, retrieval, or full dispatch verification.

## Research Question

Can RAG Studio's real scanner preserve identifiable included content, excluded-content boundaries, Unicode content, and large-file boundaries in the assembled context it produces?

## Hypothesis

Content from files accepted by the scanner will remain present and identifiable in the resulting assembled context, while content from excluded files will not appear there.

## Scope

The experiment tests the real `FileScannerWorker` and its context assembly path using a controlled synthetic fixture.

It observes:

- files discovered;
- files included;
- files excluded;
- read failures;
- identifiable content markers;
- Unicode content;
- beginning and ending markers in a deliberately large file;
- redaction behaviour;
- resulting token count.

The test does not modify the scanner's production behaviour.

## Explicit Non-Goals

This experiment does not:

- change scanner semantics;
- introduce chunking or retrieval;
- test Ollama dispatch;
- test the GUI signal-to-handler path;
- establish cross-platform UI or rendering correctness;
- establish retrieval omission versus display truncation;
- use customer or private project data.

## Automated Evidence

The integration test is located at:

`tests/test_context_continuity.py`

It creates a temporary synthetic project fixture containing controlled included and excluded files, including Unicode and deliberately large content with identifiable boundary markers.

The test passes the fixture through the real `FileScannerWorker` and checks the resulting assembled context.

The test verifies that:

- included content markers are present;
- Unicode content survives assembly;
- the deliberately large file retains both its beginning and ending markers;
- excluded-file content does not appear in assembled context;
- scanner file counts remain consistent;
- no read failures occur.

The test uses only temporary synthetic data and does not depend on a customer project.

## Result

The experiment's local automated suite passed:

- **26 passed**
- **0 failures**
- **0 errors**
- local runtime: **0.14 seconds** when run from the `tests` directory.

GitHub Actions independently completed successfully on the experiment branch after the Linux CI runtime dependency was corrected.

The successful CI run was:

- workflow: **RAG Studio Tests**
- run: **#12**
- commit: `f11aa4a874ffa6976dda9133b3e871ebffa53e95`
- conclusion: **success**

The immediately preceding CI run containing the Linux runtime correction also succeeded:

- commit: `b6d425360ebcd3557ef78c460679783a72398d6f`
- run: **#11**
- conclusion: **success**

The earlier CI failure was a collection-time environment error caused by missing `libEGL.so.1`, not a failed test assertion. The workflow was updated to install the Ubuntu/Debian EGL runtime package `libegl1`, after which CI completed successfully.

## Interpretation

The evidence supports the hypothesis for the tested assembly boundary.

The real scanner preserved the identifiable included content and large-file boundaries while excluding the controlled unmatched file content. Unicode content also survived the assembly path.

This provides evidence that the scanner's current whole-directory assembly path does not silently remove the tested content before the resulting `assembled_text` is produced.

The result does **not** establish:

- that the GUI displays all assembled content correctly;
- that the context survives unchanged into the final AI payload;
- that Ollama receives exactly the same context;
- cross-platform reproducibility;
- retrieval behaviour, because the current implementation uses whole-directory context assembly rather than conventional retrieval/chunking;
- behaviour for every possible file encoding or file size.

## Reproducibility

Relevant implementation and evidence:

- `main_ui.py` — `FileScannerWorker` and assembled-context construction;
- `lib/redactor.py` — existing redaction implementation;
- `lib/token_counter.py` — token measurement;
- `tests/test_context_continuity.py` — controlled assembly-continuity test;
- `TESTING.md` — external testing and reporting workflow.

The fixture is generated inside the test. No customer source, credentials, private paths, or external project data are required.

## Evidence Boundary

The tested boundary is:

**synthetic filesystem → real FileScannerWorker → assembled context**

The next untested boundary is:

**assembled context → `compiled_context` → final dispatch payload**

That boundary is the subject proposed for Experiment 002-B.

## Follow-Up Research Question

Does the context stored by RAG Studio after scanning remain unchanged when it is incorporated into the final payload sent to the local AI service?

This is the proposed next experiment and is not part of the current result.

## Relationship to Issue #5

Issue #5 remains the broader QA tracking point.

Context Assembly Continuity 002-A provides the next traceable layer:

**Issue #5 → Experiment 001 scanner observation → Experiment 002-A context assembly → Experiment 002-B dispatch continuity**

Each experiment preserves its own research question, evidence, boundary, and unresolved next step.
