# AI-PACK v2.0 — User Manual

## PRODUCT OVERVIEW & MISSION

AI-Pack v2.0 is a local-first, privacy-focused context orchestrator designed to solve the bottleneck around context congestion and token roll-off/overflow crashes that can occur when using large language models. It ensures local data is used to perform AI tasks, protecting corporate intellectual property locally. AI-Pack v2.0 helps developers and businesses manage and analyze their codebase, ensuring that sensitive information is secured before it reaches the local AI model on your laptop or desktop.

## ⚙️ SYSTEM REQUIREMENTS & INSTALLATION (Arch Linux)

### Local Runtime Infrastructure

**Software Requirements:**
- **Python venv:** This is a virtual environment that allows you to isolate Python applications and their dependencies.
- **Pacman Dependencies:** `qt6-base` and `noto-fonts`. These packages provide the necessary graphical user interface components and fonts for AI-Pack v2.0.
- **Local Ollama Runner:** This is a service that runs the Qwen2.5-coder:3b model locally. Ensure that the Qwen2.5-coder:3b model is installed and running on your CPU.

**Installation Steps:**

1. **Create a Python Virtual Environment:**
   ```bash
   python3 -m venv ai-pack-env
   source ai-pack-env/bin/activate
   ```

2. **Install Ollama:**
   Follow the Ollama installation instructions for your architecture: [Ollama Installation Guide](https://ollama.io/docs/install/).

3. **Install Required Packages:**
   ```bash
   sudo pacman -S qt6-base noto-fonts
   ```

4. **Run the Ollama Runner:**
   Ensure that the Qwen2.5-coder:3b model is running locally. You can start the runner by running the following command:
   ```bash
   ollama run qwen2.5-coder:3b
   ```

5. **Verify Installation:**
   You can verify that the Ollama runner is running by accessing the Ollama API endpoint:
   ```bash
   curl http://localhost:11434/api
   ```

## 🎛️ CORE FEATURE OPERATIONS

### 🛡️ Automated Data Compliance & Token Telemetry Tracking

RAG Studio / AI Wrapper enforces absolute transparency by introducing a real-time **Data Compliance Status Column** across all system telemetry feeds and exported corporate audit logs. 

Instead of operating as a traditional "black-box" script, the framework evaluates incoming directory streams sequentially inside system memory, providing a convenient, truthful overview of your repository's data hygiene without risking corporate trade secrets.

| Parameter Tracker | Metric Profile | Functional Logic |
| :--- | :--- | :--- |
| 🟢 **CLEAN / VERIFIED LOCAL** | Secure Payload | Text stream passed verbatim through RAM; zero compliance leaks detected. |
| 🔴 **[REDACTED: COMPLIANCE_MAPPING]** | Masked Threat | In-memory regex scrubbing intercepted and neutralized a hardcoded credential vector (API Keys, Passwords, or Private SSH Keys) prior to model packaging. |

#### Why This Architecture Matters:

* **Zero Refactoring Overhead:** Saves developers hours of manual cleanup by automatically neutralizing credential vectors, ensuring a codebase snapshot is instantly ready for local analysis.
  
* **Syntactic Integrity:** The substitution engine masks the raw credential string values but retains the variable names and code structures. This allows local models to debug structural variables without ever exposing active production tokens.
  
* **Audit-Ready Documentation:** When the **Corporate Audit Log Exporter** is engaged, the compliance column states are printed directly into a beautifully formatted Markdown report (`.md`) inside the local `output/` directory, serving as physical compliance evidence for security teams.


### Using the Dashboard Panel

**1. Selecting a Project Repository Folder**
   - Navigate to the dashboard panel in AI-Pack v2.0.
   - Use the file browser to select a project repository folder. AI-Pack v2.0 will automatically parse the repository and display the context track weight metrics gauge.

**2. Reading the Dynamic "Context Track Weight" Metrics Gauge**
   - The context track weight gauge provides real-time metrics on the size of the context being processed by AI-Pack v2.0. The gauge will display Green, Yellow, or Red indicators depending on the size of the context:
     - **Green:** The context size is within the acceptable range.
     - **Yellow:** The context size is approaching the acceptable range.
     - **Red:** The context size is too large and may cause token roll-off/overflow crashes.

**3. The Compliance Redaction switch**
   - The Compliance Redaction switch allows you to mask API keys and passwords in memory. This ensures that sensitive information is not exposed in the logs or output files.

**4. The Corporate Audit Log exporter**
   - The Corporate Audit Log exporter allows you to write logs directly to the output folder. This is useful for auditing and monitoring the AI-Pack v2.0 operations.

## 🛡️ DATA SECURITY & COMPLIANCE STANDARD

**1. Local Loopback Network Guarantee**
   - AI-Pack v2.0 ensures that all data is processed and stored locally, preventing data from leaving your local network.

**2. Regex Scrubbing Engine**
   - The Regex Scrubbing Engine is used to securely scrub proprietary company keys and other sensitive information from memory. This ensures that sensitive information is not exposed in the logs or output files.

## 🛠️ TROUBLESHOOTING & PIPELINE TIMEOUTS

**1. Pipeline Interface Timeout Error**
   - If a "Pipeline Interface Timeout Error" occurs, it may be due to CPU inference crunch times on large payloads. To address this, you can adjust the network deadline configurations or increase the CPU resources allocated to AI-Pack v2.0.

## Conclusion

AI-Pack v2.0 is a powerful tool designed to help developers and businesses efficiently manage and analyze their codebase. With its local-first architecture and focus on data security and compliance, AI-Pack v2.0 ensures that sensitive information is kept secure and that the AI models used are aligned with corporate standards. By following the instructions in this User Manual, you can easily deploy and understand AI-Pack v2.0 and start leveraging its powerful features to improve your development process.
