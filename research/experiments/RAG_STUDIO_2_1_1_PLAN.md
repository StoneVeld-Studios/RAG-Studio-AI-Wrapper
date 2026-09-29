# RAG Studio 2.1.1 — Context Selection & Human-Facing Context Control

## Status
Planned.
This document records the scope and intended sequence for the RAG Studio 2.1.1 upgrade. It is a planning record, not evidence that the planned changes have been implemented.

## Origin
The plan follows external QA work tracked in GitHub Issue #5: **[QA Testing] Cross-Platform UI Rendering and Context Loading Verification**.
Issue #5 asked external testers to exercise real project directories and report UI, context loading, and truncation problems.
Manual local testing then exposed a larger context-management problem:
- Guardian project: approximately 50,729 tokens (1238% of the observed context limit).
- ExperimentalOS project: approximately 109,513 tokens (2673% of the observed context limit).
- Existing selection modes did not provide enough control to reduce these projects to a useful working context.
These observations are the motivation for 2.1.1.

## Problem
RAG Studio currently assembles selected project material into one context. The scanner already excludes some common development directories, but the user has limited control over individual folders and files.
Large real-world projects can therefore produce a context far beyond the active local model limit.
The goal is not to hide this problem through silent truncation or automatic packaging. The goal is to give the user clearer, deterministic control over what becomes context.

## Research Question
Can RAG Studio provide understandable, deterministic folder/file selection and exclusion controls while making the resulting context size and dispatch impact visible to the user?

## Core Design Principle
**The project is the source. The user creates the context.**
RAG Studio should help the user understand and control selection rather than silently deciding what the AI should receive.

## Planned Context Selection Model
Selection should be hierarchical:
**Project folder → subfolders → files**
Inclusion establishes candidate context. Exclusion removes material from that candidate context.
Folder and file control should coexist rather than forcing the user to choose only broad file-type modes.

## Planned Selection Categories
### Project material
- source code
- documentation
- tests
- research
- project configuration
- build/configuration instructions

### Environment and generated material
- .venv
- virtual-environment contents
- dependency installations
- .git
- caches
- __pycache__
- build directories
- generated output
- temporary files
- compiled artifacts
- editor/system metadata

### Sensitive material
A separate concern from ordinary exclusion:
- credentials
- private keys
- secrets
- local environment values
Security redaction and context exclusion are not interchangeable. A file may be useful after sensitive values are redacted, while an environment/package file may simply be irrelevant.

## Planned User Controls
The exact UI will be designed after inspecting the current UI structure, but the intended capabilities are:
- open/load a project or data folder
- inspect discovered subfolders and files
- include or exclude folders
- include or exclude individual files
- filter by file type
- apply sensible automatic exclusions for known environment/generated material
- see included/excluded counts
- understand why material was excluded
- retain the ability to override appropriate automatic classifications
The implementation should avoid turning the interface into an unnecessarily complex file manager.

## Context Budget Visibility
The user should be able to see the effect of selection on the model context before dispatch.
Intended information includes:
- current context token count
- active model context limit
- percentage of context used
- token impact of the user's instruction
- resulting total before sending
- clear ready/warning/blocked state
The user should not have to discover an oversized request only after pressing the AI action.

## Instruction Impact
Adding or changing the user instruction should update the displayed token impact before dispatch.
Conceptually:
**Context:** 3,742 tokens
**Instruction:** +126 tokens
**Total:** 3,868 / 4,096
The exact presentation is a UI decision to be made during implementation.

## Human-Facing Language
2.1.1 should improve terminology without changing backend semantics.
Areas identified during manual testing include:
- replace highly mechanical labels such as 'Target Repository Path' with language appropriate to projects and data folders
- make the local-AI action easier to understand
- reduce unnecessary implementation terminology in the GUI
- retain backend terms such as 'redaction' where they are useful internally
- use more human-facing wording for security/protection controls
- add short descriptions where they improve clarity
- retain the existing iconography and dark visual character unless testing identifies a concrete problem
The objective is clearer communication, not a visual redesign.

## Feedback and Verification
The GUI should provide a small session feedback area for tester/user observations.
Planned capability:
**Session Feedback**
and an export action along the lines of:
**Export Session Verification Audit Trail (.md)**
The exported verification material should focus on operational facts rather than unnecessarily reproducing project/customer content.
Potential operational information includes:
- application version
- model
- context limit
- selection/filter state
- files discovered/included/excluded
- read failures
- token counts
- redaction count
- session feedback
The exact audit contents must be designed with the existing privacy boundary in mind.

## Explicit Non-Goals for 2.1.1
2.1.1 should not silently introduce:
- conventional retrieval/chunking
- automatic AI-based file importance decisions
- silent context truncation
- opaque automatic context packaging
- changes to deterministic kernel semantics
- network-dependent context selection
- customer/private test data in the repository
- unnecessary GUI redesign
Multiple context packages may be investigated later as a separate research question if evidence supports them.

## Testing Strategy
The upgrade should be developed with both automated and manual evidence.
### Automated
Add deterministic tests for:
- folder inclusion/exclusion
- file inclusion/exclusion
- file-type filtering
- automatic environment/generated exclusions
- included/excluded counts
- resulting assembled context
- token accounting
- instruction token impact
- interaction between selection and kernel observation
Synthetic fixtures should remain controlled and contain no private project data.
### Manual
Use real local projects such as Guardian and ExperimentalOS to test:
- usability of folder/file selection
- reduction of context size
- discoverability of exclusions
- clarity of explanations
- instruction/token feedback
- GUI responsiveness
- real-world project structures
The large Guardian and ExperimentalOS observations are baseline evidence for the problem, not target values that the new implementation must artificially reach.
### CI
GitHub Actions must remain part of the evidence trail. Local tests should be complemented by the repository's independent CI environment.

## Evidence and Traceability
The intended chain is:
**Issue #5** → external QA request → manual observations → context-selection problem identified → **2.1.1 plan** → implementation → automated tests → local manual testing → GitHub CI → documented results → release decision
The existing experiments remain separate evidence:
- KERNEL_LIVE_OBSERVATION_001.md
- CONTEXT_ASSEMBLY_CONTINUITY_002_A.md
This plan does not replace those records.

## Implementation Sequence
1. Inspect the current GUI structure and existing controls.
2. Convert this plan into an exact, minimal implementation/change list.
3. Design the folder/file selection model without changing scanner semantics unnecessarily.
4. Add deterministic selection/exclusion behavior.
5. Add token-budget and instruction-impact visibility.
6. Improve GUI wording and descriptions.
7. Add session feedback and verification-audit export.
8. Add/update automated tests.
9. Run the local test suite.
10. Run the application manually against controlled and real projects.
11. Run and inspect GitHub Actions.
12. Record the resulting evidence and remaining limitations.
13. Prepare the 2.1.1 release/PR only after the evidence is satisfactory.

## Release Boundary
The intended outcome is a focused **RAG Studio v2.1.1** upgrade centered on context selection, exclusion, token visibility, and clearer human-facing operation.
Version 2.1.1 should be treated as complete only when the implemented behavior, tests, manual observations, CI evidence, and documentation agree.

## Next Immediate Action
**Read-only inspection of the current GUI structure and controls.**
No implementation change should be made from this plan alone. The next implementation step should follow an explicit change list derived from the actual current UI.