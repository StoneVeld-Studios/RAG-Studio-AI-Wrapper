"""Write privacy-conscious Markdown audit evidence for a RAG Trigger Studio session."""

from dataclasses import dataclass
import os
from pathlib import Path
import tempfile


@dataclass(frozen=True)
class AuditRecord:
    """Explicit operational facts allowed in the session audit.

    Prompt text, assembled project context, and project paths are intentionally
    not fields in this record.
    """

    generated_at: str
    provider: str
    model: str
    files_selected: int
    files_available: int
    context_tokens: int
    instruction_tokens: int
    total_tokens: int
    token_limit: int
    redaction_count: int
    kernel_state: str
    kernel_reasons: tuple[str, ...]
    execution_status: str
    session_feedback: str = ""


def render_audit(record: AuditRecord) -> str:
    """Render stable Markdown from explicitly supplied session evidence."""
    allowed_statuses = {"not_started", "pending", "successful", "failed"}
    if record.execution_status not in allowed_statuses:
        raise ValueError(
            f"execution_status must be one of: {', '.join(sorted(allowed_statuses))}"
        )

    lines = [
        "# RAG Trigger Studio — Session Audit",
        "",
        f"- Generated at: {record.generated_at}",
        f"- Provider: {record.provider}",
        f"- Model: {record.model}",
        f"- Files selected: {record.files_selected} / {record.files_available}",
        f"- Context tokens: {record.context_tokens}",
        f"- Instruction tokens: {record.instruction_tokens}",
        f"- Total tokens: {record.total_tokens} / {record.token_limit}",
        f"- Redactions: {record.redaction_count}",
        f"- Kernel state: {record.kernel_state}",
        f"- Execution status: {record.execution_status}",
        "",
        "## Kernel Reasons",
    ]
    if record.kernel_reasons:
        lines.extend(f"- {reason}" for reason in record.kernel_reasons)
    else:
        lines.append("- No reasons recorded.")

    lines.extend(["", "## Session Feedback", record.session_feedback, ""])
    return "\n".join(lines)


def write_audit(path: str | Path, record: AuditRecord) -> Path:
    """Write an audit atomically; propagate failures to the caller.

    A temporary file is written beside the destination and then replaced into
    place, so a failed write does not leave a half-written final audit.
    """
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    content = render_audit(record)
    temporary_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=target.parent,
            prefix=f".{target.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)
            temporary.write(content)
            temporary.flush()
            os.fsync(temporary.fileno())

        os.replace(temporary_path, target)
        temporary_path = None
        return target
    finally:
        if temporary_path is not None:
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                pass
