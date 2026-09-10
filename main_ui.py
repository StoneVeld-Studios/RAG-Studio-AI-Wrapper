import os
import sys
import urllib.request
import json
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTextEdit, QLabel, QFileDialog,
                             QProgressBar, QCheckBox, QMessageBox, QRadioButton,
                             QButtonGroup, QLineEdit)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

# Modular package imports
from config.settings_manager import SettingsManager
from lib.runner_sync import OllamaSync
from lib.token_counter import QwenTokenCounter
from lib.redactor import SecurityRedactor


class FileScannerWorker(QThread):
    """
    Background worker thread that handles heavy repository file aggregation
    and token computation in memory to keep the main GUI from freezing.
    """
    scan_complete = pyqtSignal(str, int)

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
        files_discovered = 0
        files_included = 0
        files_excluded = 0
        read_failures = 0

        # Comprehensive extensions arrays targeting all layout focus possibilities
        if self.filter_id == 2:    # Pure Source Code Engine
            target_exts = ('.py', '.c', '.h', '.sh', '.cpp',
                           '.hpp', '.java', '.cs', '.js', '.ts', '.go', '.rs')
        elif self.filter_id == 3:  # Pure Documentation & Logs
            target_exts = ('.md', '.txt', '.log', '.json', '.yaml',
                           '.xml', '.csv', '.ini', '.conf', '.cfg', '')
        else:                      # Complete Repository Package
            target_exts = ('.py', '.c', '.h', '.sh', '.cpp', '.hpp', '.java', '.cs', '.js', '.ts', '.go', '.rs',
                           '.md', '.txt', '.log', '.json', '.yaml', '.xml', '.csv', '.ini', '.conf', '.cfg', '')

        for root, _, files in os.walk(self.folder):
            if '.venv' in root or '.git' in root or 'output' in root or '__pycache__' in root:
                continue

            for file in files:
                files_discovered += 1
                file_lower = file.lower()

                # Match target extensions or accept files without any extension tag if docs are selected
                if any(file_lower.endswith(ext) for ext in target_exts if ext) or (
                    '' in target_exts and '.' not in file
                ):
                    file_path = os.path.join(root, file)

                    try:
                        # Dual-layer robust encoding fallback reader mechanism
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                                content = f.read()
                        except Exception:
                            with open(file_path, 'r', encoding='latin-1', errors='replace') as f:
                                content = f.read()

                        if self.redact_checked or (self.custom_key and len(self.custom_key) > 2):
                            content, _ = self.redactor.scrub_text(
                                content, self.custom_key
                            )

                        rel_path = os.path.relpath(file_path, self.folder)
                        assembled_text += f"\n\n--- FILE: {rel_path} ---\n" + content
                        files_included += 1

                    except Exception as e:
                        read_failures += 1
                        print(
                            f"[Debug Link Error Pass] Skipping file read layout for: {file}. Details: {e}"
                        )
                else:
                    files_excluded += 1

        total_tokens = self.token_engine.calculate_tokens(assembled_text)
        self.scan_complete.emit(assembled_text, total_tokens)


class AIWorker(QThread):
    """Asynchronous background execution handler for local host AI processing loops."""
    response_received = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, host, model, payload):
        super().__init__()
        self.host = host
        self.model = model
        self.payload = payload

    def run(self):
        try:
            url = f"{self.host}/api/generate"
            data = json.dumps(
                {"model": self.model, "prompt": self.payload, "stream": False}).encode('utf-8')
            req = urllib.request.Request(url, data=data, headers={
                                         'Content-Type': 'application/json'}, method='POST')
            with urllib.request.urlopen(req, timeout=600) as resp:
                response_data = json.loads(resp.read().decode())
                self.response_received.emit(response_data.get(
                    "response", "No response emitted."))
        except Exception as e:
            self.error_occurred.emit(str(e))


class RAGStudioApp(QWidget):
    """Universal High-Performance Offline AI Content Orchestration Workspace."""

    def __init__(self):
        super().__init__()
        self.settings = SettingsManager()
        self.sync_engine = OllamaSync(self.settings.get("ollama_host"))
        self.token_engine = QwenTokenCounter()

        self.active_folder = ""
        self.compiled_context = ""
        self.active_model = self.settings.get("target_model")
        self.max_tokens = self.sync_engine.get_active_context_limit(
            self.active_model)

        self.initUI()
        self.apply_dark_mode_theme()

    def initUI(self):
        self.setWindowTitle('RAG Studio / AI Wrapper - v2.1.0 Core Terminal')
        self.resize(1000, 700)

        main_layout = QHBoxLayout()
        left_panel = QVBoxLayout()
        right_panel = QVBoxLayout()

        self.btn_select_dir = QPushButton("📂 Target Repository Path")
        self.btn_select_dir.setFont(
            QFont('DejaVu Sans', 10, QFont.Weight.Bold))
        self.btn_select_dir.clicked.connect(self.select_directory)

        self.lbl_path = QLabel("System Storage Track: Standby")
        self.lbl_path.setWordWrap(True)

        lbl_filter_heading = QLabel("📦 Content Extraction Focus:")
        lbl_filter_heading.setFont(QFont('DejaVu Sans', 9, QFont.Weight.Bold))

        self.filter_group = QButtonGroup(self)
        self.rad_all = QRadioButton("Complete Manifest (All Records)")
        self.rad_code = QRadioButton("Pure Source Code Engine")
        self.rad_docs = QRadioButton("Pure Documentation & Logs")
        self.rad_all.setChecked(True)

        # Explicitly assign immutable positive IDs to resolve the -1 PyQt6 default bug
        self.filter_group.addButton(self.rad_all, 1)
        self.filter_group.addButton(self.rad_code, 2)
        self.filter_group.addButton(self.rad_docs, 3)
        self.filter_group.idClicked.connect(self.trigger_background_scan)

        lbl_security_heading = QLabel("🛡️ Security & Privacy Parameters:")
        lbl_security_heading.setFont(
            QFont('DejaVu Sans', 9, QFont.Weight.Bold))

        self.chk_redact = QCheckBox("Enforce Automated Pattern Redaction")
        self.chk_redact.setChecked(self.settings.get("auto_redact_secrets"))
        self.chk_redact.stateChanged.connect(self.trigger_background_scan)

        self.lbl_custom_key = QLabel("Precision Custom Redaction Mask String:")
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
        left_panel.addStretch()
        left_panel.addWidget(self.lbl_token_count)
        left_panel.addWidget(self.progress_tokens)

        self.lbl_prompt = QLabel(
            "Enter Prompt Instructions or Structural Targets:")
        self.txt_prompt = QTextEdit()
        self.txt_prompt.setPlaceholderText(
            "Describe the operational analysis requested from the localized environment model...")
        self.txt_prompt.setMaximumHeight(100)

        self.btn_dispatch = QPushButton(
            "⚡ Execute Context Synchronization & Query")
        self.btn_dispatch.setFont(QFont('DejaVu Sans', 10, QFont.Weight.Bold))
        self.btn_dispatch.clicked.connect(self.execute_pipeline)

        self.lbl_console = QLabel("Offline Target AI Telemetry Core:")
        self.txt_console = QTextEdit()
        self.txt_console.setReadOnly(True)
        self.txt_console.setFont(QFont('DejaVu Sans Mono', 10))
        self.txt_console.setPlaceholderText(
            "Decoded data records and prompt generation loops stream output here...")

        self.btn_save_response = QPushButton(
            "💾 Export AI Response Matrix (.md)")
        self.btn_save_response.setEnabled(False)
        self.btn_save_response.clicked.connect(self.export_response_file)

        right_panel.addWidget(self.lbl_prompt)
        right_panel.addWidget(self.txt_prompt)
        right_panel.addWidget(self.btn_dispatch)
        right_panel.addSpacing(5)
        right_panel.addWidget(self.lbl_console)
        right_panel.addWidget(self.txt_console)
        right_panel.addWidget(self.btn_save_response)

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
            self.lbl_path.setText(f"Active Folder: {os.path.basename(folder)}")
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

    def handle_scan_complete(self, assembled_text, total_tokens):
        """Triggered smoothly when background thread completes traversal calculations."""
        self.compiled_context = assembled_text

        # Calculate true contextual progress metrics tracking loop
        pct = int((total_tokens / self.max_tokens) *
                  100) if self.max_tokens > 0 else 0
        self.lbl_token_count.setText(
            f"Context Footprint: {total_tokens} / {self.max_tokens} Tokens ({pct}% Full)")
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

    def execute_pipeline(self):
        user_prompt = self.txt_prompt.toPlainText().strip()
        if not user_prompt:
            QMessageBox.warning(self, "Validation Warning",
                                "Please input processing instructions.")
            return

        final_payload = f"Context Material For Analysis:\n{self.compiled_context}\n\nUser Instruction:\n{user_prompt}"
        total_tokens = self.token_engine.calculate_tokens(final_payload)

        if total_tokens > self.max_tokens:
            QMessageBox.critical(self, "Pipeline Blocked",
                                 "Context weight exceeds backend parameters.")
            return

        self.txt_console.setText(
            "Transmitting context package pipeline through local loopback network array...")
        self.btn_dispatch.setEnabled(False)
        self.btn_save_response.setEnabled(False)

        if self.chk_audit.isChecked():
            self.generate_corporate_audit_log(user_prompt, total_tokens)

        self.worker = AIWorker(self.settings.get(
            "ollama_host"), self.settings.get("target_model"), final_payload)
        self.worker.response_received.connect(self.handle_ai_response)
        self.worker.error_occurred.connect(self.handle_pipeline_error)
        self.worker.start()

    def generate_corporate_audit_log(self, prompt, tokens):
        output_dir = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), "output")
        os.makedirs(output_dir, exist_ok=True)
        log_path = os.path.join(output_dir, "context_sync_audit.md")
        try:
            with open(log_path, 'w', encoding='utf-8') as f:
                f.write("# RAG STUDIO: Automation Verification Audit Log\n")
                f.write(
                    f"**Data Pipeline Metrics:** {tokens} / {self.max_tokens} Context Tokens Allocated\n\n")
                f.write("## 📝 Instruction Profile Query\n> " + prompt + "\n\n")
                f.write("## 🗄️ Transmitted Storage Manifest Payload\n```text\n" +
                        self.compiled_context + "\n```\n")
        except Exception:
            pass

    def handle_ai_response(self, response_text):
        self.txt_console.setText(response_text)
        self.btn_dispatch.setEnabled(True)
        self.btn_save_response.setEnabled(True)

    def handle_pipeline_error(self, error_msg):
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
