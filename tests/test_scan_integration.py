import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PyQt6.QtWidgets import QApplication, QTreeWidget
from PyQt6.QtCore import Qt

from main_ui import FileScannerWorker, RAGStudioApp, ScanResult
from lib.kernel import Kernel, KernelState, Observation


QT_APP = QApplication.instance() or QApplication([])


def _find_item(item, path_parts):
    if not path_parts:
        return item
    for index in range(item.childCount()):
        child = item.child(index)
        if child.text(0) == path_parts[0]:
            return _find_item(child, path_parts[1:])
    return None


def test_scan_exposes_automatic_exclusions_and_per_file_redactions(tmp_path):
    included_file = tmp_path / "included.py"
    excluded_file = tmp_path / "excluded.bin"
    excluded_dir = tmp_path / ".git"
    excluded_dir.mkdir()
    (excluded_dir / "internal.py").write_text("ignored", encoding="utf-8")

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

    scan_result = results[0]
    assert "excluded.bin" in scan_result.excluded_paths
    assert ".git" in scan_result.excluded_paths
    assert scan_result.file_redactions["included.py"] == 1


def test_project_tree_supports_folder_selection_partial_state_and_exclusions():
    app = RAGStudioApp.__new__(RAGStudioApp)
    app.active_folder = "/tmp/project"
    app.context_files = {
        "src/a.py": "a",
        "src/b.py": "b",
        "README.md": "readme",
    }
    app.scan_result = ScanResult(
        assembled_text="",
        files_discovered=4,
        files_included=3,
        files_excluded=1,
        read_failures=0,
        redaction_count=0,
        token_count=0,
        file_contents=app.context_files,
        excluded_paths=("src/generated.bin", ".git"),
        file_redactions={"src/a.py": 0, "src/b.py": 0, "README.md": 0},
    )
    app.tree = QTreeWidget()
    app.selected_files = set(app.context_files)
    app.rebuild_context = lambda: None
    app.evaluate_final_context = lambda: None
    app.build_project_tree()

    root = app.tree.topLevelItem(0)
    src = _find_item(root, ["src"])
    a_file = _find_item(root, ["src", "a.py"])
    generated = _find_item(root, ["src", "generated.bin"])

    assert root.checkState(0) == Qt.CheckState.Checked
    assert src.checkState(0) == Qt.CheckState.Checked
    assert generated.isDisabled()
    assert generated.text(1) == "Excluded automatically"

    a_file.setCheckState(0, Qt.CheckState.Unchecked)
    app.handle_tree_change(a_file, 0)
    assert src.checkState(0) == Qt.CheckState.PartiallyChecked
    assert app.selected_files == {"src/b.py", "README.md"}

    src.setCheckState(0, Qt.CheckState.Unchecked)
    app.handle_tree_change(src, 0)
    assert src.checkState(0) == Qt.CheckState.Unchecked
    assert app.selected_files == {"README.md"}

    src.setCheckState(0, Qt.CheckState.Checked)
    app.handle_tree_change(src, 0)
    assert src.checkState(0) == Qt.CheckState.Checked
    assert app.selected_files == {"src/a.py", "src/b.py", "README.md"}


def test_kernel_observes_final_selected_context_not_full_scan():
    app = RAGStudioApp.__new__(RAGStudioApp)
    app.selected_files = {"a.py"}
    app.compiled_context = "a"
    app.context_files = {"a.py": "a", "b.py": "b"}
    app.max_tokens = 100
    app.scan_result = ScanResult(
        assembled_text="a b",
        files_discovered=3,
        files_included=2,
        files_excluded=1,
        read_failures=0,
        redaction_count=2,
        token_count=2,
        file_contents=app.context_files,
        excluded_paths=("excluded.bin",),
        file_redactions={"a.py": 1, "b.py": 1},
    )
    app.kernel = Kernel()
    app.token_engine = type(
        "TokenEngine", (), {"calculate_tokens": staticmethod(lambda text: len(text))}
    )()
    app.diagnostics = None
    app.evaluate_final_context()

    observation = app.kernel_result.observation
    assert observation.files_discovered == 3
    assert observation.files_included == 1
    assert observation.files_excluded == 2
    assert observation.redaction_count == 1
    assert observation.token_count == 1
    assert app.kernel_result.state == KernelState.SAFE
