# 🛠 Autonomous Code Debugger — Agentic RAG

An **Agentic Retrieval-Augmented Generation** system that autonomously diagnoses Python runtime errors from logs, retrieves context from documentation, generates minimal patches, executes patches in a sandbox, and validates fixes — iterating until resolved.

Built with **Python, LangChain, Anthropic Claude, Chroma, SentenceTransformers, Streamlit, and optional Docker sandboxing**.

---

## 📌 Features
- **Semantic Doc Retrieval**: Index your PDFs/TXT docs into a persistent Chroma vector DB for context-aware debugging.
- **Agentic Workflow**:
  - **RetrieverAgent** — retrieves relevant docs
  - **RootCauseAgent** — summarizes probable causes
  - **PatchGeneratorAgent** — validates logs, generates minimal Python patches
  - **ExecutionAgent** — sandboxed execution (local/Docker)
  - **ValidatorAgent** — validates patch success
- **Strict Input Validation**: Only attempts patches if input matches Python traceback patterns.
- **Iteration Until Fixed**: Automatically retries with updated context until the bug is fixed or max attempts reached.
- **Streamlit UI**: Paste logs, upload files, and view patch history with results.

---

## 🗂️ Project Structure
```
autonomous-code-debugger/
│
├── agents/                         # Individual AI agents for each debugging stage
│   ├── retriever_agent.py           # Retrieves relevant context from ChromaDB
│   ├── root_cause_agent.py          # Summarizes probable error causes
│   ├── patch_generator_agent.py     # Validates error & generates minimal patch
│   ├── execution_agent.py           # Executes patch in sandbox/local environment
│   └── validator_agent.py           # Validates if fix was successful
│
├── rag/                             # RAG-related components
│   ├── vector_store.py              # Handles Chroma vector DB creation & updates
│   ├── retriever.py                 # Vector search utilities
│   └── document_loader.py           # Loads and preprocesses docs into the vector store
│
├── Scripts/
│   └── build_index.py               # Script to index documentation into Chroma DB
│
├── ui/
│   └── app.py                       # Streamlit UI for running the debugger
│
├── data/
│   ├── docs/                        # Documentation files (PDF/TXT) for context
│   └── vector_db/                   # Persistent Chroma database
│
├── screenshots/                     # Screenshots for Outputs
│
├── test_inputs/                     # Sample error logs and code snippets for testing
│
├── graph.py                         # Orchestrates agent workflow
├── config.py                        # Configuration & API keys
├── requirements.txt                 # Python dependencies
└── README.md                        # Project documentation
```
📜 License
MIT — free to use, modify, and share.