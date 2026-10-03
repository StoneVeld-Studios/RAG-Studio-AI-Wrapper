from dataclasses import fields

import pytest

from lib.audit_log import AuditRecord, write_audit


def make_record(**overrides):
    values = {
        "generated_at": "2026-10-03T10:00:00+02:00",
        "provider": "Test Core",
        "model": "deterministic-test",
        "files_discovered": 7,
        "files_selected": 3,
        "files_available": 5,
        "files_excluded": 2,
        "read_failures": 0,
        "context_tokens": 120,
        "instruction_tokens": 15,
        "total_tokens": 135,
        "token_limit": 4096,
        "redaction_count": 2,
        "kernel_state": "SAFE",
        "kernel_reasons": (
            "Token count is within context limit.",
            "File counts are consistent.",
        ),
        "execution_status": "pending",
        "session_feedback": "Unicode rendering looks correct.",
    }
    values.update(overrides)
    return AuditRecord(**values)


def test_audit_contains_operational_facts_and_submitted_feedback(tmp_path):
    target = tmp_path / "output" / "context_sync_audit.md"

    write_audit(target, make_record())

    report = target.read_text(encoding="utf-8")
    assert "Provider: Test Core" in report
    assert "Model: deterministic-test" in report
    assert "Files discovered: 7" in report
    assert "Files selected: 3 / 5" in report
    assert "Files excluded: 2" in report
    assert "File read failures: 0" in report
    assert "Context tokens: 120" in report
    assert "Instruction tokens: 15" in report
    assert "Total tokens: 135 / 4096" in report
    assert "Redactions: 2" in report
    assert "Kernel state: SAFE" in report
    assert "Execution status: pending" in report
    assert "Unicode rendering looks correct." in report


def test_audit_is_deterministic_for_the_same_record(tmp_path):
    record = make_record()
    first = tmp_path / "first.md"
    second = tmp_path / "second.md"

    write_audit(first, record)
    write_audit(second, record)

    assert first.read_bytes() == second.read_bytes()


def test_audit_record_contract_has_no_prompt_context_or_path_fields():
    field_names = {field.name for field in fields(AuditRecord)}

    assert "session_feedback" in field_names
    assert "provider" in field_names
    assert "kernel_state" in field_names
    assert "prompt" not in field_names
    assert "context" not in field_names
    assert "project_path" not in field_names
    assert "file_contents" not in field_names


def test_audit_write_failure_is_not_silently_swallowed(tmp_path):
    parent_is_file = tmp_path / "not-a-directory"
    parent_is_file.write_text("fixture", encoding="utf-8")
    target = parent_is_file / "audit.md"

    with pytest.raises(OSError):
        write_audit(target, make_record())


def test_audit_records_execution_status_without_claiming_success(tmp_path):
    target = tmp_path / "audit.md"

    write_audit(target, make_record(execution_status="failed"))

    report = target.read_text(encoding="utf-8")
    assert "Execution status: failed" in report
    assert "Execution status: successful" not in report


def test_audit_rejects_unknown_execution_status(tmp_path):
    with pytest.raises(ValueError, match="execution_status"):
        write_audit(
            tmp_path / "audit.md",
            make_record(execution_status="complete-ish"),
        )
