import os
import sys
from dataclasses import dataclass
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTextEdit, QLabel, QFileDialog,
                             QProgressBar, QCheckBox, QMessageBox, QRadioButton,
                             QButtonGroup, QLineEdit, QTreeWidget, QTreeWidgetItem, QPlainTextEdit)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

# Modular package imports
from config.settings_manager import SettingsManager
from lib.token_counter import QwenTokenCounter
from lib.core import CoreRequest, CoreResponse
from lib.core_providers import OllamaCoreProvider
from lib.redactor import SecurityRedactor
from lib.kernel import Kernel, Observation
from lib.audit_log import AuditRecord, write_audit


@dataclass(frozen=True)
class ScanResult:
    assembled_text: str
    files_discovered: int
    files_included: int
    files_excluded: int
    read_failures: int
    redaction_count: int
    token_count: int
    file_contents: dict
    excluded_paths: tuple
    file_redactions: dict


class FileScannerWorker(QThread):
    """
    Background worker thread that handles heavy repository file aggregation
    and token computation in memory to keep the main GUI from freezing.
    """
    scan_complete = pyqtSignal(object)

    def __init__(self, folder, filter_id, redact_checked, custom_key):
        super().__init__()
        self.folder = folder
        self.filter_id = int(filter_id)  # Enforce clean integer mapping
        self.redact_checked = redact_checked
        self.custom_key = custom_key
        self.redactor = SecurityRedactor()
        self.token_engine = QwenTokenCounter()

    def run(self):
        assembled_text = ""
        file_contents = {}
        files_discovered = 0
        files_included = 0
        files_excluded = 0
        read_failures = 0
        redaction_count = 0
        excluded_paths = []
        file_redactions = {}
        excluded_dir_names = {'.venv', '.git', 'output', '__pycache__'}

        # Comprehensive extensions arrays targeting all layout focus possibilities
        if self.filter_id == 2:    # Pure Source Code Engine
            target_exts = ('.py', '.c', '.h', '.sh', '.cpp',
                           '.hpp', '.java', '.cs', '.js', '.ts', '.go', '.rs')
        elif self.filter_id == 3:  # Pure Documentation & Logs
            target_exts = ('.md', '.txt', '.log', '.json', '.jsonl', '.yaml',
                           '.xml', '.csv', '.ini', '.conf', '.cfg', '')
        else:                      # Complete Repository Package
            target_exts = ('.py', '.c', '.h', '.sh', '.cpp', '.hpp', '.java', '.cs', '.js', '.ts', '.go', '.rs',
                           '.md', '.txt', '.log', '.json', '.jsonl', '.yaml', '.xml', '.csv', '.ini', '.conf', '.cfg', '')

        for root, dirs, files in os.walk(self.folder):
            kept_dirs = []
            for directory in dirs:
                if directory in excluded_dir_names:
                    excluded_paths.append(os.path.relpath(
                        os.path.join(root, directory), self.folder
                    ))
                else:
                    kept_dirs.append(directory)
            dirs[:] = kept_dirs

            for file in files:
                files_discovered += 1
                file_lower = file.lower()
                file_path = os.path.join(root, file)

                # Match target extensions or accept files without any extension tag if docs are selected
                if any(file_lower.endswith(ext) for ext in target_exts if ext) or (
                    '' in target_exts and '.' not in file
                ):
                    try:
                        # Dual-layer robust encoding fallback reader mechanism
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                                content = f.read()
                        except Exception:
                            with open(file_path, 'r', encoding='latin-1', errors='replace') as f:
                                content = f.read()

                        file_redaction_count = 0
                        if self.redact_checked or (self.custom_key and len(self.custom_key) > 2):
                            content, file_redaction_count = self.redactor.scrub_text(
                                content, self.custom_key
                            )
                            redaction_count += file_redaction_count

                        rel_path = os.path.relpath(file_path, self.folder)
                        file_contents[rel_path] = content
                        file_redactions[rel_path] = file_redaction_count
                        assembled_text += f"\n\n--- FILE: {rel_path} ---\n" + content
                        files_included += 1

                    except Exception as e:
                        read_failures += 1
                        print(
                            f"[Debug Link Error Pass] Skipping file read layout for: {file}. Details: {e}"
                        )
                else:
                    files_excluded += 1
                    excluded_paths.append(os.path.relpath(file_path, self.folder))

        total_tokens = self.token_engine.calculate_tokens(assembled_text)
        self.scan_complete.emit(
            ScanResult(
                assembled_text=assembled_text,
                files_discovered=files_discovered,
                files_included=files_included,
                files_excluded=files_excluded,
                read_failures=read_failures,
                redaction_count=redaction_count,
                token_count=total_tokens,
                file_contents=file_contents,
                excluded_paths=tuple(sorted(set(excluded_paths))),
                file_redactions=file_redactions,
            )
        )


class CoreWorker(QThread):
    """Asynchronous execution handler for the engine-neutral Core boundary."""
    response_received = pyqtSignal(object)
    error_occurred = pyqtSignal(str)

    def __init__(self, core, request):
        super().__init__()
        self.core = core
        self.request = request

    def run(self):
        try:
            response = self.core.generate(self.request)
            self.response_received.emit(response)
        except Exception as e:
            self.error_occurred.emit(str(e))


class RAGStudioApp(QWidget):
    """Universal High-Performance Offline AI Content Orchestration Workspace."""

    def __init__(self):
        super().__init__()
        self.settings = SettingsManager()
        self.core = OllamaCoreProvider(
            host=self.settings.get("ollama_host"),
            model=self.settings.get("target_model"),
            context_limit=self.settings.get("fallback_context_cap"),
        )
        self.token_engine = QwenTokenCounter()

        self.active_folder = ""
        self.compiled_context = ""
        self.context_files = {}
        self.selected_files = set()
        self.scan_result = None
        self.last_response = None
        self.active_model = self.settings.get("target_model")
        self.max_tokens = self.core.context_limit()
        self.kernel = Kernel()
        self.kernel_result = None
        self.submitted_feedback = []

        self.initUI()
        self.apply_dark_mode_theme()

    def initUI(self):
        self.setWindowTitle('RAG Trigger Studio - v2.1.1')
        self.resize(1200, 800)

        main_layout = QHBoxLayout()
        left_panel = QVBoxLayout()
        right_panel = QVBoxLayout()

        self.btn_select_dir = QPushButton("📂 Target Repository Path")
        self.btn_select_dir.setFont(
            QFont('DejaVu Sans', 10, QFont.Weight.Bold))
        self.btn_select_dir.clicked.connect(self.select_directory)

        self.lbl_core = QLabel(f"Core: Configured — {self.core.provider_name}")
        self.lbl_core.setWordWrap(True)
        self.lbl_path = QLabel("Project: Standby")
        self.lbl_path.setWordWrap(True)

        lbl_filter_heading = QLabel("Project Contents:")
        lbl_filter_heading.setFont(QFont('DejaVu Sans', 9, QFont.Weight.Bold))

        self.filter_group = QButtonGroup(self)
        self.rad_all = QRadioButton("All supported project material")
        self.rad_code = QRadioButton("Source code")
        self.rad_docs = QRadioButton("Documentation & logs")
        self.rad_all.setChecked(True)

        # Explicitly assign immutable positive IDs to resolve the -1 PyQt6 default bug
        self.filter_group.addButton(self.rad_all, 1)
        self.filter_group.addButton(self.rad_code, 2)
        self.filter_group.addButton(self.rad_docs, 3)
        self.filter_group.idClicked.connect(self.trigger_background_scan)

        lbl_security_heading = QLabel("Protection:")
        lbl_security_heading.setFont(
            QFont('DejaVu Sans', 9, QFont.Weight.Bold))

        self.chk_redact = QCheckBox("Protect detected secrets")
        self.chk_redact.setChecked(self.settings.get("auto_redact_secrets"))
        self.chk_redact.stateChanged.connect(self.trigger_background_scan)

        self.lbl_custom_key = QLabel("Additional value to protect:")
        self.txt_custom_key = QLineEdit()
        self.txt_custom_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_custom_key.setPlaceholderText(
            "Enter target API Keys or strings to scrub...")
        self.txt_custom_key.textChanged.connect(self.trigger_background_scan)

        self.chk_audit = QCheckBox(
            "Export Session Verification Audit Trail (.md)")
        self.chk_audit.setChecked(self.settings.get("export_audit_logs"))

        self.lbl_token_count = QLabel(
            f"Context Footprint: 0 / {self.max_tokens} Tokens")
        self.progress_tokens = QProgressBar()
        self.progress_tokens.setMaximum(self.max_tokens)

        left_panel.addWidget(self.lbl_core)
        left_panel.addWidget(self.btn_select_dir)
        left_panel.addWidget(self.lbl_path)
        left_panel.addSpacing(10)
        left_panel.addWidget(lbl_filter_heading)
        left_panel.addWidget(self.rad_all)
        left_panel.addWidget(self.rad_code)
        left_panel.addWidget(self.rad_docs)
        left_panel.addSpacing(10)
        left_panel.addWidget(lbl_security_heading)
        left_panel.addWidget(self.chk_redact)
        left_panel.addWidget(self.lbl_custom_key)
        left_panel.addWidget(self.txt_custom_key)
        left_panel.addWidget(self.chk_audit)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Project Contents", "State"])
        self.tree.itemChanged.connect(self.handle_tree_change)
        left_panel.addWidget(self.tree, stretch=1)
        left_panel.addStretch()
        self.lbl_instruction_tokens = QLabel("Instruction: +0 tokens")
        self.lbl_total_tokens = QLabel(f"Total before send: 0 / {self.max_tokens}")
        left_panel.addWidget(self.lbl_token_count)
        left_panel.addWidget(self.lbl_instruction_tokens)
        left_panel.addWidget(self.lbl_total_tokens)
        left_panel.addWidget(self.progress_tokens)

        self.lbl_prompt = QLabel(
            "Enter Prompt Instructions or Structural Targets:")
        self.txt_prompt = QTextEdit()
        self.txt_prompt.setPlaceholderText(
            "Describe the operational analysis requested from the localized environment model...")
        self.txt_prompt.setMaximumHeight(100)
        self.txt_prompt.textChanged.connect(self.update_instruction_budget)

        self.btn_dispatch = QPushButton("Run with Local AI")
        self.btn_dispatch.setFont(QFont('DejaVu Sans', 10, QFont.Weight.Bold))
        self.btn_dispatch.clicked.connect(self.execute_pipeline)

        self.lbl_console = QLabel("Core Response:")
        self.txt_console = QTextEdit()
        self.txt_console.setReadOnly(True)
        self.txt_console.setFont(QFont('DejaVu Sans Mono', 10))
        self.txt_console.setPlaceholderText("The response from your local Core will appear here...")

        self.btn_save_response = QPushButton(
            "💾 Export AI Response Matrix (.md)")
        self.btn_save_response.setEnabled(False)
        self.btn_save_response.clicked.connect(self.export_response_file)

        self.feedback_label = QLabel("Session Feedback:")
        self.feedback = QPlainTextEdit()
        self.feedback.setPlaceholderText("What did you observe? What worked or failed?")
        self.feedback.setMaximumHeight(90)
        self.btn_submit_feedback = QPushButton("Submit Feedback")
        self.btn_submit_feedback.clicked.connect(self.submit_feedback)
        self.lbl_feedback_status = QLabel("Feedback has not been submitted.")
        self.lbl_feedback_status.setWordWrap(True)
        self.btn_diagnostics = QPushButton("Developer Diagnostics")
        self.btn_diagnostics.setCheckable(True)
        self.btn_diagnostics.toggled.connect(self.toggle_diagnostics)
        self.diagnostics = QPlainTextEdit()
        self.diagnostics.setReadOnly(True)
        self.diagnostics.setMaximumHeight(130)
        self.diagnostics.setVisible(False)

        right_panel.addWidget(self.lbl_prompt)
        right_panel.addWidget(self.txt_prompt)
        right_panel.addWidget(self.btn_dispatch)
        right_panel.addSpacing(5)
        right_panel.addWidget(self.lbl_console)
        right_panel.addWidget(self.txt_console)
        right_panel.addWidget(self.btn_save_response)
        right_panel.addWidget(self.feedback_label)
        right_panel.addWidget(self.feedback)
        right_panel.addWidget(self.btn_submit_feedback)
        right_panel.addWidget(self.lbl_feedback_status)
        right_panel.addWidget(self.btn_diagnostics)
        right_panel.addWidget(self.diagnostics)

        main_layout.addLayout(left_panel, stretch=2)
        main_layout.addLayout(right_panel, stretch=3)
        self.setLayout(main_layout)

    def apply_dark_mode_theme(self):
        self.setStyleSheet("""
            QWidget { background-color: #121212; color: #e0e0e0; font-family: 'DejaVu Sans', sans-serif; }
            QPushButton { background-color: #1a73e8; border: 1px solid #1a73e8; border-radius: 4px; padding: 10px; color: #ffffff; }
            QPushButton:hover { background-color: #1557b0; }
            QPushButton:disabled { background-color: #2c2c2c; color: #757575; border-color: #333333; }
            QTextEdit, QLineEdit { background-color: #1e1e1e; border: 1px solid #333333; border-radius: 4px; color: #34a853; padding: 6px; }
            QProgressBar { border: 1px solid #333333; border-radius: 4px; text-align: center; background-color: #1e1e1e; color: #ffffff; font-weight: bold; }
        """)

    def select_directory(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Open Repository Footprint")
        if folder:
            self.active_folder = folder
            self.lbl_path.setText(f"Project: {os.path.basename(folder)}")
            self.lbl_core.setText(f"Core: Connected — {self.core.provider_name}")
            self.trigger_background_scan()

    def trigger_background_scan(self):
        """Dispatches the asynchronous file scanner to keep the UI fluid and track values cleanly."""
        if not self.active_folder:
            return

        self.lbl_token_count.setText("Scanning folder paths in background...")
        self.btn_select_dir.setEnabled(False)
        self.btn_dispatch.setEnabled(False)

        # Fetch the explicit integer ID to pass down to the background scanning core
        current_filter_id = self.filter_group.checkedId()

        self.scanner = FileScannerWorker(
            self.active_folder,
            current_filter_id,
            self.chk_redact.isChecked(),
            self.txt_custom_key.text()
        )
        self.scanner.scan_complete.connect(self.handle_scan_complete)
        self.scanner.start()

    def handle_scan_complete(self, scan_result):
        """Triggered smoothly when background thread completes traversal calculations."""
        self.scan_result = scan_result
        self.context_files = scan_result.file_contents
        self.selected_files = set(self.context_files)
        self.build_project_tree()
        self.rebuild_context()
        self.evaluate_final_context()

        # Calculate true contextual progress metrics tracking loop
        total_tokens = self.token_engine.calculate_tokens(self.compiled_context)
        pct = int((total_tokens / self.max_tokens) *
                  100) if self.max_tokens > 0 else 0
        self.lbl_token_count.setText(
            f"Context: {total_tokens} / {self.max_tokens} tokens ({pct}% full)")
        self.progress_tokens.setValue(min(total_tokens, self.max_tokens))

        if total_tokens > self.max_tokens:
            self.progress_tokens.setStyleSheet(
                "QProgressBar::chunk { background-color: #ea4335; }")
        elif total_tokens > (self.max_tokens - self.settings.get("safety_buffer_tokens")):
            self.progress_tokens.setStyleSheet(
                "QProgressBar::chunk { background-color: #fbbc05; }")
        else:
            self.progress_tokens.setStyleSheet(
                "QProgressBar::chunk { background-color: #34a853; }")

        self.btn_select_dir.setEnabled(True)
        self.btn_dispatch.setEnabled(True)


    def build_project_tree(self):
        self.tree.blockSignals(True)
        self.tree.clear()

        root_name = os.path.basename(self.active_folder) or self.active_folder
        root = QTreeWidgetItem([root_name, "Project"])
        root.setFlags(
            root.flags()
            | Qt.ItemFlag.ItemIsUserCheckable
        )
        root.setCheckState(0, Qt.CheckState.Checked)
        root.setToolTip(0, "Select or clear all available project material.")
        self.tree.addTopLevelItem(root)

        nodes = {"": root}
        all_paths = set(self.context_files) | set(self.scan_result.excluded_paths)

        for rel_path in sorted(all_paths):
            parent = root
            key = ""
            parts = rel_path.split(os.sep)
            is_excluded = rel_path in set(self.scan_result.excluded_paths)

            for index, part in enumerate(parts):
                key = os.path.join(key, part) if key else part
                is_leaf = index == len(parts) - 1

                if key not in nodes:
                    item = QTreeWidgetItem([part, "Excluded automatically" if is_excluded and is_leaf else "Folder"])
                    parent.addChild(item)
                    nodes[key] = item

                    if is_excluded and is_leaf:
                        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                        item.setCheckState(0, Qt.CheckState.Unchecked)
                        item.setDisabled(True)
                        item.setToolTip(
                            0,
                            "Excluded automatically by the current project scan. "
                            "This material cannot be selected for context."
                        )
                    else:
                        item.setFlags(
                            item.flags()
                            | Qt.ItemFlag.ItemIsUserCheckable
                        )
                        item.setCheckState(0, Qt.CheckState.Checked)
                        item.setToolTip(
                            0,
                            "Select this folder to include all selectable files beneath it."
                        )

                parent = nodes[key]

            if not is_excluded:
                parent.setData(0, Qt.ItemDataRole.UserRole, rel_path)
                parent.setText(1, "Included")

        root.setExpanded(True)
        self.tree.blockSignals(False)

    def _set_descendant_state(self, item, state):
        for index in range(item.childCount()):
            child = item.child(index)
            if child.isDisabled():
                continue
            child.setCheckState(0, state)
            self._set_descendant_state(child, state)

    def _collect_selected_files(self, item):
        path = item.data(0, Qt.ItemDataRole.UserRole)
        if path in self.context_files and item.childCount() == 0:
            if item.checkState(0) == Qt.CheckState.Checked:
                self.selected_files.add(path)
            item.setText(1, "Included" if item.checkState(0) == Qt.CheckState.Checked else "Not selected")
            return

        for index in range(item.childCount()):
            self._collect_selected_files(item.child(index))

    def _update_parent_states(self, item):
        if item.childCount() == 0 or item.isDisabled():
            return item.checkState(0)

        child_states = []
        for index in range(item.childCount()):
            child = item.child(index)
            if child.isDisabled():
                continue
            child_states.append(self._update_parent_states(child))

        if not child_states:
            return item.checkState(0)

        if all(state == Qt.CheckState.Checked for state in child_states):
            state = Qt.CheckState.Checked
        elif all(state == Qt.CheckState.Unchecked for state in child_states):
            state = Qt.CheckState.Unchecked
        else:
            state = Qt.CheckState.PartiallyChecked

        item.setCheckState(0, state)
        return state

    def handle_tree_change(self, item, column):
        if column != 0 or item.isDisabled():
            return

        self.tree.blockSignals(True)
        if item.childCount() > 0:
            state = item.checkState(0)
            if state == Qt.CheckState.PartiallyChecked:
                state = Qt.CheckState.Unchecked
                item.setCheckState(0, state)
            self._set_descendant_state(item, state)

        self.selected_files.clear()
        for index in range(self.tree.topLevelItemCount()):
            root = self.tree.topLevelItem(index)
            self._update_parent_states(root)
            self._collect_selected_files(root)

        self.tree.blockSignals(False)
        self.rebuild_context()
        self.evaluate_final_context()

    def evaluate_final_context(self):
        if self.scan_result is None:
            self.kernel_result = None
            return

        selected_count = len(self.selected_files)
        deselected_count = max(self.scan_result.files_included - selected_count, 0)
        selected_redactions = sum(
            self.scan_result.file_redactions.get(path, 0)
            for path in self.selected_files
        )
        final_token_count = self.token_engine.calculate_tokens(self.compiled_context)

        observation = Observation(
            files_discovered=self.scan_result.files_discovered,
            files_included=selected_count,
            files_excluded=self.scan_result.files_excluded + deselected_count,
            read_failures=self.scan_result.read_failures,
            redaction_count=selected_redactions,
            token_count=final_token_count,
            token_limit=self.max_tokens,
        )
        self.kernel_result = self.kernel.evaluate(observation)
        self.update_diagnostics()

    def rebuild_context(self):
        self.compiled_context = "".join(
            f"\n\n--- FILE: {path} ---\n{self.context_files[path]}"
            for path in sorted(self.selected_files)
        )
        self.update_token_display()
        self.update_diagnostics()

    def update_token_display(self):
        context_tokens = self.token_engine.calculate_tokens(self.compiled_context)
        instruction_tokens = self.token_engine.calculate_tokens(self.txt_prompt.toPlainText().strip())
        total_tokens = context_tokens + instruction_tokens
        self.lbl_token_count.setText(f"Context: {context_tokens} / {self.max_tokens} tokens")
        self.lbl_instruction_tokens.setText(f"Instruction: +{instruction_tokens} tokens")
        self.lbl_total_tokens.setText(f"Total before send: {total_tokens} / {self.max_tokens}")
        self.progress_tokens.setValue(min(context_tokens, self.max_tokens))

    def update_instruction_budget(self):
        self.update_token_display()

    def toggle_diagnostics(self, visible):
        self.diagnostics.setVisible(visible)
        if visible:
            self.update_diagnostics()

    def update_diagnostics(self):
        if not hasattr(self, "diagnostics") or not self.diagnostics.isVisible():
            return
        context_tokens = self.token_engine.calculate_tokens(self.compiled_context)
        instruction_tokens = self.token_engine.calculate_tokens(self.txt_prompt.toPlainText().strip())
        kernel_state = (
            self.kernel_result.state.value
            if self.kernel_result
            else "waiting for scan"
        )
        kernel_allowed = (
            str(self.kernel_result.allowed)
            if self.kernel_result
            else "not evaluated"
        )
        observations = (
            self.kernel_result.observations
            if self.kernel_result
            else {}
        )
        kernel_reasons = (
            "; ".join(self.kernel_result.reasons)
            if self.kernel_result
            else "No Kernel evaluation available."
        )
        self.diagnostics.setPlainText(
            f"Provider: {self.core.provider_name}\n"
            f"Model: {self.core.model}\n"
            f"Context limit: {self.max_tokens}\n"
            f"Files selected: {len(self.selected_files)} / {len(self.context_files)}\n"
            f"Files discovered: {observations.get('files_discovered', 'unknown')}\n"
            f"Files excluded: {observations.get('files_excluded', 'unknown')}\n"
            f"Read failures: {observations.get('read_failures', 'unknown')}\n"
            f"Redactions: {observations.get('redaction_count', 'unknown')}\n"
            f"Context tokens: {context_tokens}\n"
            f"Instruction tokens: {instruction_tokens}\n"
            f"Kernel state: {kernel_state}\n"
            f"Kernel allowed: {kernel_allowed}\n"
            f"Kernel reasons: {kernel_reasons}"
        )

    def execute_pipeline(self):
        user_prompt = self.txt_prompt.toPlainText().strip()
        if not user_prompt:
            QMessageBox.warning(self, "Validation Warning",
                                "Please input processing instructions.")
            return

        total_tokens = self.token_engine.calculate_tokens(self.compiled_context) + self.token_engine.calculate_tokens(user_prompt)

        if total_tokens > self.max_tokens:
            QMessageBox.critical(self, "Pipeline Blocked",
                                 "Context weight exceeds backend parameters.")
            return

        self.txt_console.setText(
            "Running with Local AI Core...")
        self.btn_dispatch.setEnabled(False)
        self.btn_save_response.setEnabled(False)

        if self.chk_audit.isChecked():
            if not self.generate_corporate_audit_log(user_prompt, total_tokens, "pending"):
                self.txt_console.setText(
                    "Execution not started: the requested session audit could not be written."
                )
                self.btn_dispatch.setEnabled(True)
                return

        self.worker = CoreWorker(
            self.core,
            CoreRequest(context=self.compiled_context, instructions=user_prompt),
        )
        self.worker.response_received.connect(self.handle_ai_response)
        self.worker.error_occurred.connect(self.handle_pipeline_error)
        self.worker.start()

    def submit_feedback(self):
        """Retain an explicit tester observation without adding it to AI context."""
        feedback_text = self.feedback.toPlainText().strip()
        if not feedback_text:
            self.lbl_feedback_status.setText(
                "No feedback submitted. Enter an observation first."
            )
            return

        submitted_at = datetime.now().astimezone().isoformat(timespec="seconds")
        self.submitted_feedback.append((submitted_at, feedback_text))
        self.feedback.clear()
        self.lbl_feedback_status.setText(
            "Feedback submitted for this session. It remains separate from AI context "
            "and will be written to the audit when a run starts with audit export enabled."
        )

    def generate_corporate_audit_log(self, prompt, tokens, execution_status="pending"):
        """Write the session's operational evidence without recording prompt/context text."""
        if not self.chk_audit.isChecked():
            return True

        output_dir = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), "output")
        log_path = os.path.join(output_dir, "context_sync_audit.md")
        context_tokens = self.token_engine.calculate_tokens(self.compiled_context)
        instruction_tokens = self.token_engine.calculate_tokens(prompt)
        kernel_result = self.kernel_result
        observations = kernel_result.observations if kernel_result else {}

        feedback_text = "\n\n---\n\n".join(
            f"**Submitted at:** {submitted_at}\n\n{content}"
            for submitted_at, content in self.submitted_feedback
        )

        record = AuditRecord(
            generated_at=datetime.now().astimezone().isoformat(timespec="seconds"),
            provider=self.core.provider_name,
            model=self.core.model,
            files_discovered=observations.get("files_discovered", len(self.context_files)),
            files_selected=len(self.selected_files),
            files_available=len(self.context_files),
            files_excluded=observations.get("files_excluded", 0),
            read_failures=observations.get("read_failures", 0),
            context_tokens=context_tokens,
            instruction_tokens=instruction_tokens,
            total_tokens=tokens,
            token_limit=self.max_tokens,
            redaction_count=observations.get("redaction_count", 0),
            kernel_state=kernel_result.state.value if kernel_result else "UNAVAILABLE",
            kernel_reasons=kernel_result.reasons if kernel_result else (),
            execution_status=execution_status,
            session_feedback=feedback_text,
        )

        try:
            write_audit(log_path, record)
        except OSError as error:
            self.lbl_feedback_status.setText(
                f"Audit export failed: {error}. Submitted feedback remains in this session."
            )
            lifecycle_message = (
                "The AI request has not been started."
                if execution_status == "pending"
                else f"The recorded execution status is '{execution_status}', but the final audit update failed."
            )
            QMessageBox.warning(
                self,
                "Audit Export Failed",
                "The session audit could not be written. "
                f"{lifecycle_message} Submitted feedback remains in this session.\n\n"
                f"Details: {error}",
            )
            return False

        self.lbl_feedback_status.setText(
            f"Audit updated: {os.path.relpath(log_path, os.path.dirname(os.path.abspath(__file__)))} "
            f"({execution_status})."
        )
        return True

    def handle_ai_response(self, response: CoreResponse):
        self.last_response = response
        if self.chk_audit.isChecked():
            self.generate_corporate_audit_log(
                self.txt_prompt.toPlainText().strip(),
                self.token_engine.calculate_tokens(self.compiled_context)
                + self.token_engine.calculate_tokens(self.txt_prompt.toPlainText().strip()),
                "successful",
            )
        self.txt_console.setText(response.text)
        self.lbl_core.setText(f"Core: Connected — {response.provider} / {response.model}")
        self.update_diagnostics()
        self.btn_dispatch.setEnabled(True)
        self.btn_save_response.setEnabled(True)

    def handle_pipeline_error(self, error_msg):
        if self.chk_audit.isChecked():
            prompt = self.txt_prompt.toPlainText().strip()
            self.generate_corporate_audit_log(
                prompt,
                self.token_engine.calculate_tokens(self.compiled_context)
                + self.token_engine.calculate_tokens(prompt),
                "failed",
            )
        self.txt_console.setText(
            f"Pipeline Interface Error: Connection to local loopback host failed.\nDetails: {error_msg}")
        self.btn_dispatch.setEnabled(True)

    def export_response_file(self):
        text_content = self.txt_console.toPlainText()
        if not text_content:
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Report Manifest", "ai_response_report.md", "Markdown Documents (*.md)")
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(text_content)
                QMessageBox.information(
                    self, "Export Successful", "Data report written cleanly.")
            except Exception as e:
                QMessageBox.critical(self, "File Action Blocked", str(e))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = RAGStudioApp()
    ex.show()
    sys.exit(app.exec())
