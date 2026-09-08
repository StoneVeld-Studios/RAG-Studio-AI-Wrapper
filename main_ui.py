import os
import sys
import urllib.request
import json
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QTextEdit, QLabel, QFileDialog, 
                             QProgressBar, QCheckBox, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

# Import your custom modular tracking engines cleanly from your directories
from config.settings_manager import SettingsManager
from lib.runner_sync import OllamaSync
from lib.token_counter import QwenTokenCounter
from lib.redactor import SecurityRedactor

class AIWorker(QThread):
    """
    Background worker thread ensuring local AI communications run asynchronously.
    This keeps the main UI interface perfectly smooth and responsive.
    """
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
            data = json.dumps({
                "model": self.model,
                "prompt": self.payload,
                "stream": False
            }).encode('utf-8')
            
            req = urllib.request.Request(
                url, data=data, 
                headers={'Content-Type': 'application/json'}, 
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=600) as resp:
                response_data = json.loads(resp.read().decode())
                self.response_received.emit(response_data.get("response", "No response text found."))
        except Exception as e:
            self.error_occurred.emit(str(e))


class StoneVeldAIPackApp(QWidget):
    """Main graphical native user interface layer for AI-Pack v2."""
    def __init__(self):
        super().__init__()
        # Initialize modules
        self.settings = SettingsManager()
        self.sync_engine = OllamaSync(self.settings.get("ollama_host"))
        self.token_engine = QwenTokenCounter()
        self.redactor = SecurityRedactor()
        
        # Runtime variables
        self.active_folder = ""
        self.compiled_context = ""
        self.max_tokens = self.sync_engine.get_active_context_limit(self.settings.get("target_model"))
        
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('StoneVeld AI-Pack v2.0 - Core Dashboard')
        self.resize(900, 650)
        
        main_layout = QHBoxLayout()
        left_panel = QVBoxLayout()
        right_panel = QVBoxLayout()
        
        # --- Left Control Panel Layout ---
        self.btn_select_dir = QPushButton("📂 Select Project Folder")
        self.btn_select_dir.setStyleSheet("padding: 8px; font-weight: bold;")
        self.btn_select_dir.clicked.connect(self.select_directory)
        
        self.lbl_path = QLabel("Workspace Status: Inactive")
        self.lbl_path.setWordWrap(True)
        
        # Options Group
        self.chk_redact = QCheckBox("🛡️ Enforce Compliance Redaction")
        self.chk_redact.setChecked(self.settings.get("auto_redact_secrets"))
        
        self.chk_audit = QCheckBox("🗄️ Export Corporate Audit Log (.md)")
        self.chk_audit.setChecked(self.settings.get("export_audit_logs"))
        
        # Token Capacity Metrics Gauges
        self.lbl_token_count = QLabel(f"Context Track weight: 0 / {self.max_tokens} Tokens")
        self.progress_tokens = QProgressBar()
        self.progress_tokens.setMaximum(self.max_tokens)
        
        left_panel.addWidget(self.btn_select_dir)
        left_panel.addWidget(self.lbl_path)
        left_panel.addWidget(self.chk_redact)
        left_panel.addWidget(self.chk_audit)
        left_panel.addStretch()
        left_panel.addWidget(self.lbl_token_count)
        left_panel.addWidget(self.progress_tokens)
        
        # --- Right Interactive Console Layout ---
        self.lbl_prompt = QLabel("Enter your structural query or prompt instructions:")
        self.txt_prompt = QTextEdit()
        self.txt_prompt.setPlaceholderText("e.g., Analyze this codebase context layout for memory handling leaks...")
        self.txt_prompt.setMaximumHeight(120)
        
        self.btn_dispatch = QPushButton("🚀 Run Orchestration & Query AI")
        self.btn_dispatch.setStyleSheet("background-color: #1a73e8; color: white; padding: 10px; font-weight: bold;")
        self.btn_dispatch.clicked.connect(self.execute_pipeline)
        
        self.lbl_console = QLabel("Local AI Engine Response Stream:")
        self.txt_console = QTextEdit()
        self.txt_console.setReadOnly(True)
        self.txt_console.setPlaceholderText("Direct offline model responses will display here...")
        
        right_panel.addWidget(self.lbl_prompt)
        right_panel.addWidget(self.txt_prompt)
        right_panel.addWidget(self.btn_dispatch)
        right_panel.addWidget(self.lbl_console)
        right_panel.addWidget(self.txt_console)
        
        # Integrate complete application view
        main_layout.addLayout(left_panel, stretch=1)
        main_layout.addLayout(right_panel, stretch=2)
        self.setLayout(main_layout)
    def select_directory(self):
        folder = QFileDialog.getExistingDirectory(self, "Open Repository Directory")
        if folder:
            self.active_folder = folder
            self.lbl_path.setText(f"Active Folder: {os.path.basename(folder)}")
            self.process_context_in_memory()

    def process_context_in_memory(self):
        """Assembles data payload strings entirely in RAM to keep system execution fast."""
        if not self.active_folder:
            return

        assembled_text = ""
        target_exts = ('.py', '.c', '.h', '.sh', '.md', '.txt', '.log')
        
        for root, _, files in os.walk(self.active_folder):
            if '.venv' in root or '.git' in root or 'output' in root:
                continue
            for file in files:
                if file.endswith(target_exts):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Apply local compliance scrubbing text configurations dynamically if checked
                        if self.chk_redact.isChecked():
                            content, _ = self.redactor.scrub_text(content)
                            
                        rel_path = os.path.relpath(file_path, self.active_folder)
                        assembled_text += f"\n\n--- FILE: {rel_path} ---\n{content}"
                    except Exception:
                        pass
                        
        self.compiled_context = assembled_text
        
        # Calculate tokens using your high-accuracy library logic
        total_tokens = self.token_engine.calculate_tokens(assembled_text)
        
        # Update metrics interface gauges dynamically
        self.lbl_token_count.setText(f"Context weight: {total_tokens} / {self.max_tokens} Tokens")
        self.progress_tokens.setValue(min(total_tokens, self.max_tokens))
        
        # Visual color warnings based on token limit thresholds
        if total_tokens > self.max_tokens:
            self.progress_tokens.setStyleSheet("QProgressBar::chunk { background-color: #d93025; }")
        elif total_tokens > (self.max_tokens - self.settings.get("safety_buffer_tokens")):
            self.progress_tokens.setStyleSheet("QProgressBar::chunk { background-color: #f9ab00; }")
        else:
            self.progress_tokens.setStyleSheet("QProgressBar::chunk { background-color: #1e8e3e; }")

    def execute_pipeline(self):
        if not self.compiled_context:
            QMessageBox.warning(self, "Validation Error", "Please select a valid directory context layout first.")
            return
            
        user_prompt = self.txt_prompt.toPlainText().strip()
        if not user_prompt:
            QMessageBox.warning(self, "Validation Error", "Please input an analytical instruction message for the local AI.")
            return

        # Dynamically pack and wrap payloads into context boundaries inside system memory
        final_payload = f"Context Material For Analysis:\n{self.compiled_context}\n\nUser Instruction:\n{user_prompt}"
        
        # Final token safety check to protect Qwen from roll-off crashes
        total_tokens = self.token_engine.calculate_tokens(final_payload)
        if total_tokens > self.max_tokens:
            QMessageBox.critical(self, "Execution Blocked", "Total payload exceeds local context limits. Please shrink target folder size.")
            return

        self.txt_console.setText("Communicating with local engine... Please wait...")
        self.btn_dispatch.setEnabled(False)

        # Handle the Optional Corporate Audit Log Generation
        if self.chk_audit.isChecked():
            self.generate_corporate_audit_log(user_prompt, total_tokens)

        # Fire off the worker thread to query Ollama without locking the window view
        self.worker = AIWorker(
            self.settings.get("ollama_host"),
            self.settings.get("target_model"),
            final_payload
        )
        self.worker.response_received.connect(self.handle_ai_response)
        self.worker.error_occurred.connect(self.handle_pipeline_error)
        self.worker.start()

    def generate_corporate_audit_log(self, prompt, tokens):
        """Generates clean, professionally formatted Markdown audit logs inside output/ folder."""
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
        os.makedirs(output_dir, exist_ok=True)
        
        log_path = os.path.join(output_dir, "context_sync_audit.md")
        
        try:
            with open(log_path, 'w', encoding='utf-8') as f:
                f.write("# AI-PACK v2: Corporate Synchronization Audit Log\n")
                f.write(f"**Target Model:** {self.settings.get('target_model')} | **Host Address:** {self.settings.get('ollama_host')}\n\n")
                f.write("## 📊 Package Inventory Metrics\n")
                f.write(f"* **Total Context Space Allocated:** {tokens} / {self.max_tokens} Tokens\n")
                f.write(f"* **Compliance Redaction Profile Active:** {self.chk_redact.isChecked()}\n\n")
                f.write("## 📝 Instruction Query Intention\n")
                f.write(f"> {prompt}\n\n")
                f.write("## 🗄️ Transmitted Payload Manifest\n")
                f.write("```text\n" + self.compiled_context + "\n```\n")
        except Exception as e:
            print(f"Audit log file operations failed: {e}")

    def handle_ai_response(self, response_text):
        self.txt_console.setText(response_text)
        self.btn_dispatch.setEnabled(True)

    def handle_pipeline_error(self, error_msg):
        self.txt_console.setText(f"Pipeline Interface Error: Cannot connect to local Ollama runner.\nDetails: {error_msg}\n\nEnsure 'ollama serve' is running in your terminal.")
        self.btn_dispatch.setEnabled(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = StoneVeldAIPackApp()
    ex.show()
    sys.exit(app.exec())
