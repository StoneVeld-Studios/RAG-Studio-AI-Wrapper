import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from main_ui import FileScannerWorker
from lib.kernel import Kernel, KernelState, Observation


def test_real_scan_produces_kernel_observation(tmp_path):
    included_file = tmp_path / "included.py"
    excluded_file = tmp_path / "excluded.bin"

    included_file.write_text(
        "Authorization: Bearer SECRET\nprint('hello')\n",
        encoding="utf-8",
    )
    excluded_file.write_bytes(b"not source code")

    worker = FileScannerWorker(
        str(tmp_path),
        filter_id=2,
        redact_checked=False,
        custom_key="SECRET",
    )
    worker.token_engine.calculate_tokens = lambda text: 42

    results = []
    worker.scan_complete.connect(results.append)

    worker.run()

    assert len(results) == 1

    scan_result = results[0]
    assert scan_result.files_discovered == 2
    assert scan_result.files_included == 1
    assert scan_result.files_excluded == 1
    assert scan_result.read_failures == 0
    assert scan_result.redaction_count == 1
    assert scan_result.token_count == 42
    assert "SECRET" not in scan_result.assembled_text

    result = Kernel().evaluate(
        observation=Observation(
            files_discovered=scan_result.files_discovered,
            files_included=scan_result.files_included,
            files_excluded=scan_result.files_excluded,
            read_failures=scan_result.read_failures,
            redaction_count=scan_result.redaction_count,
            token_count=scan_result.token_count,
            token_limit=4096,
        )
    )

    assert result.state == KernelState.SAFE
    assert result.allowed is True
