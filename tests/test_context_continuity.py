import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from main_ui import FileScannerWorker


def test_context_assembly_preserves_included_content_and_excludes_unmatched_files(tmp_path, monkeypatch):
    short_marker = "CONTEXT_CONTINUITY_SHORT_002"
    source_marker = "CONTEXT_CONTINUITY_SOURCE_002"
    unicode_marker = "CONTEXT_CONTINUITY_UNICODE_002"
    excluded_marker = "CONTEXT_CONTINUITY_EXCLUDED_002"
    large_start = "CONTEXT_CONTINUITY_LARGE_START_002"
    large_end = "CONTEXT_CONTINUITY_LARGE_END_002"

    (tmp_path / "notes.txt").write_text(
        f"short content {short_marker}\n",
        encoding="utf-8",
    )
    (tmp_path / "sample.py").write_text(
        f"print({source_marker!r})\n",
        encoding="utf-8",
    )
    (tmp_path / "unicode.txt").write_text(
        f"Unicode: café, naïve, 日本語, 🚀 — {unicode_marker}\n",
        encoding="utf-8",
    )
    (tmp_path / "large.txt").write_text(
        large_start + "\n" + ("0123456789abcdef\n" * 20000) + large_end + "\n",
        encoding="utf-8",
    )
    (tmp_path / "excluded.bin").write_text(
        f"this must not be assembled: {excluded_marker}\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "main_ui.QwenTokenCounter.calculate_tokens",
        lambda self, text: len(text),
    )

    worker = FileScannerWorker(
        str(tmp_path),
        filter_id=0,
        redact_checked=False,
        custom_key="",
    )

    results = []
    worker.scan_complete.connect(results.append)
    worker.run()

    assert len(results) == 1
    scan_result = results[0]

    assert scan_result.files_discovered == 5
    assert scan_result.files_included == 4
    assert scan_result.files_excluded == 1
    assert scan_result.read_failures == 0
    assert scan_result.redaction_count == 0

    assembled = scan_result.assembled_text

    assert short_marker in assembled
    assert source_marker in assembled
    assert unicode_marker in assembled
    assert large_start in assembled
    assert large_end in assembled
    assert excluded_marker not in assembled

    assert scan_result.token_count == len(assembled)
