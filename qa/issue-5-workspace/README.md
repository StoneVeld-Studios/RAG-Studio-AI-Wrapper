# Issue #5 QA Test Workspace

This workspace is synthetic test material for RAG Trigger Studio.

## Purpose

Use this folder when testing context loading, file selection, automatic exclusions, redaction, JSONL handling, and context-size behaviour.

The files contain no real customer, account, credential, or personal information.

## Safe reporting

A tester may report results produced from this workspace without exposing their own project files.

Useful evidence includes:
- operating system and Python version
- application behaviour and visible errors
- selected files
- token/context counts
- diagnostic output
- terminal traces that contain only this workspace's synthetic data

Do not add personal or customer data to this workspace before sharing it.

## Expected material

The workspace deliberately contains:
- ordinary source and documentation files
- a JSONL fixture
- a synthetic bearer-like value for redaction testing
- automatically excluded directories
- an unsupported binary-like fixture represented as text content with an excluded extension
