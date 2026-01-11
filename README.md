# OmniAct (v0.1.0)

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Rust](https://img.shields.io/badge/rust-2024-orange.svg)

**OmniAct** is a next-generation Autonomous AI Agent designed for robust UI automation. Unlike traditional selector-based bots, OmniAct uses **Visual Large Language Models (VLMs)** to "see" and understand interfaces like a human, combined with a **Rust-powered self-healing** mechanism to ensure reliability.

**Author:** [StarsUnsurpass](https://github.com/StarsUnsurpass)  
**Project Repository:** [https://github.com/StarsUnsurpass/OmniAct](https://github.com/StarsUnsurpass/OmniAct)

---

## 🚀 Key Features

*   **🧠 Vision-First Intelligence:** Uses GPT-4o or Claude 3.5 Sonnet to interpret screenshots using a **Set-of-Mark (SoM)** visual prompting technique, allowing interaction with canvas, dynamic UIs, and obscure frameworks.
*   **🛡️ Rust-Powered Self-Healing:** A high-performance Rust extension (`vision_core`) performs millisecond-level pixel difference analysis. If an action fails to change the screen state, the agent automatically detects the failure and retries.
*   **⚙️ LangGraph Orchestration:** Built on a formal state machine (graph) architecture, supporting complex logic, loops, memory persistence (`thread_id`), and conditional branching.
*   **👁️ Dual-Channel Perception:** Combines visual understanding with an **OCR-like DOM Text Map**, eliminating hallucinations when reading small or blurry text.
*   **🔧 Local Tool Use (MCP-Style):** The agent can read/write files and interact with the local system, transforming it from a viewer to a worker.
*   **🤝 Human-in-the-Loop (HITL):** Automatically pauses and requests human intervention via CLI when encountering repeated failures or high-risk decisions.
*   **🐳 Sandboxed Execution:** Fully Dockerized environment for safe and reproducible runs.

---

## 🏗️ Architecture

The project follows a Polyglot Monorepo structure:

*   **`agent/` (Python):** The "Brain". Handles logic, VLM communication, and Playwright automation.
*   **`crates/vision_core/` (Rust):** The "Muscle". A compiled Python extension for heavy image processing and state verification.
*   **`agent/core/graph.py`:** The LangGraph state machine definition.

---

## 🛠️ Installation & Usage

### Prerequisites
*   Python 3.10+
*   Rust (latest stable)
*   Docker (Optional, for sandboxing)

### Local Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/StarsUnsurpass/OmniAct.git
    cd OmniAct
    ```

2.  **Initialize Environment (Build Rust Extension & Install Deps):**
    ```bash
    chmod +x setup.sh
    ./setup.sh
    ```

3.  **Configure API Keys:**
    Copy `.env.example` to `.env` and add your keys:
    ```bash
    cp .env.example .env
    # Edit .env and set OPENAI_API_KEY or ANTHROPIC_API_KEY
    ```

4.  **Run the Agent:**
    ```bash
    python agent/main.py
    ```

### Docker Usage (Sandboxed)

```bash
docker-compose up --build
```

---

## 🗺️ Roadmap

- [x] Hybrid Python + Rust Architecture
- [x] Visual Perception (SoM) & OCR
- [x] LangGraph State Machine
- [x] Self-Healing (Pixel Diff)
- [x] Basic System Tools (File I/O)
- [ ] **Model Context Protocol (MCP)** Support for standardized tool sharing.
- [ ] **Web Dashboard** for real-time monitoring.
- [ ] **Voice Interface** for multimodal interaction.

---

## 📄 License

This project is licensed under the MIT License.