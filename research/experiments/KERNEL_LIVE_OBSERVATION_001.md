# Kernel Live Observation 001

## Status

Completed implementation and automated evidence for the stated observation boundary.

## Origin and Tracking

This experiment was created in response to **Issue #5 — [QA Testing] Cross-Platform UI Rendering and Context Loading Verification**.

Issue #5 identifies the broader external-testing problem. This experiment addresses one specific foundation within that problem: whether RAG Studio's existing deterministic kernel can observe and evaluate facts produced by the real folder scanner without changing kernel semantics or application authority.

Issue #5 remains open. This experiment does **not** claim to complete the cross-platform UI, rendering, or full context-loading verification requested by the issue.

## Research Question

Can the existing deterministic RAG Studio kernel observe and evaluate facts produced by the real folder scanner without changing kernel semantics or changing which component controls AI dispatch?

## Hypothesis

The existing kernel can evaluate a real scan observation constructed from facts already produced by RAG Studio, without requiring changes to the kernel's decision semantics.

## Scope

The experiment:

- connects real scanner results to the existing kernel observation contract;
- captures the redaction count already returned by the security redactor;
- packages scanner facts in a typed `ScanResult`;
- constructs an existing `Observation` from those facts;
- evaluates the observation with the existing deterministic `Kernel`;
- retains the resulting `KernelResult` in the application for observation.

## Explicit Non-Goals

This experiment does not:

- change `Kernel` or `Observation` semantics;
- make the kernel access the filesystem;
- make the kernel access the network or Ollama;
- give the kernel GUI responsibilities;
- make the kernel authoritative over AI dispatch;
- redesign the scanner;
- introduce a second observation stage;
- introduce monitoring UI;
- introduce a Qt GUI testing framework.

## Implementation

The live application path was extended in `main_ui.py`.

The scanner now produces a typed `ScanResult` containing:

- assembled context;
- files discovered;
- files included;
- files excluded;
- read failures;
- redaction count;
- token count.

The application constructs an existing `Observation` from those facts and the active model token limit, then evaluates it through the existing kernel.

The existing final-payload token-limit check remains unchanged and continues to control dispatch. The kernel result is therefore observational in this experiment rather than an unapproved replacement for existing application authority.

## Automated Evidence

The integration test is located at:

`tests/test_scan_integration.py`

It exercises the real `FileScannerWorker` and the real `Kernel` using a temporary synthetic fixture.

The fixture contains:

- one included Python file containing a bearer credential pattern;
- one binary/non-text file that is excluded by the scanner filter.

The test verifies:

- 2 files discovered;
- 1 file included;
- 1 file excluded;
- 0 read failures;
- 1 redaction;
- deterministic token count of 42;
- the redacted secret is absent from assembled context;
- the resulting observation evaluates to `SAFE`;
- the kernel allows the observation.

The token counter is replaced only inside the test with a deterministic test value so the integration assertion does not depend on tokenizer availability or model-specific tokenization.

## Result

The experiment established that the existing deterministic kernel can evaluate facts produced by the real RAG Studio scanner without changing the kernel's semantics.

The application also contains the live observation wiring from scanner result to kernel evaluation.

The complete local test suite passed:

- **25 passed**
- **0 failures**
- **0 errors**

The branch contains three commits beyond `main` and is not behind `main`.

## Evidence Boundary

The automated integration test does **not** instantiate the complete `RAGStudioApp` or directly exercise the full Qt signal-to-handler path:

`FileScannerWorker.scan_complete` → `RAGStudioApp.handle_scan_complete` → `Observation` → `Kernel.evaluate()`

That application path is implemented, but the GUI-level signal/handler boundary remains untested by the current automated test.

Therefore the experiment establishes **observation-contract compatibility**, not complete GUI-path verification.

## Interpretation

The evidence supports the hypothesis for the tested boundary.

It does not establish:

- cross-platform UI correctness;
- UI rendering correctness;
- context display correctness;
- long-file truncation behaviour;
- retrieval omission versus display truncation;
- cross-platform reproducibility;
- tester workflow correctness.

Those remain part of the broader Issue #5 testing problem.

## Reproducibility

Relevant implementation and evidence:

- `main_ui.py` — live scanner-to-kernel observation wiring;
- `lib/kernel.py` — existing deterministic kernel;
- `lib/redactor.py` — existing redaction implementation;
- `tests/test_kernel.py` — existing kernel behaviour tests;
- `tests/test_scan_integration.py` — live scanner/kernel integration evidence.

The test fixture is synthetic and generated within the test. No customer directory, customer source, credentials, or private diagnostic data is required.

## Follow-Up Research Question

What is the smallest trustworthy way to exercise or observe the remaining scanner-signal-to-application-handler boundary without introducing unnecessary GUI test infrastructure?

This is a research question for a future experiment, not an authorization to expand the current implementation.

## Relationship to Issue #5

Issue #5 remains the broader QA tracking point.

Kernel Live Observation 001 should be read as one traceable experiment within that issue:

**Issue #5 → research question → implementation → automated evidence → documented boundary → next experiment**

The experiment provides evidence for one layer of the QA architecture while explicitly preserving the unresolved portions of the original issue.
