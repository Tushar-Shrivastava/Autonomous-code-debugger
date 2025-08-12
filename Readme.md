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
## Screenshots:- 

<img width="1859" height="866" alt="Code_debugger_ui" src="https://github.com/user-attachments/assets/d64ef187-e85a-46ba-8ffd-4c8b49d86674" />
<img width="684" height="795" alt="Building_vector_store" src="https://github.com/user-attachments/assets/89dbc55c-34ff-4e42-9779-f8f9ca11d829" />
<img width="1733" height="642" alt="Attempt_3" src="https://github.com/user-attachments/assets/f726fdcf-52a7-4825-b560-7f6eb2e27733" />
<img width="1139" height="712" alt="Attempt_2" src="https://github.com/user-attachments/assets/647324cb-613c-4f85-b4fa-af812ff5cb93" />
<img width="1829" height="746" alt="Attempt_1" src="https://github.com/user-attachments/assets/85ebaa0c-aead-4f04-9f96-e84e75a27f2c" />
<img width="659" height="472" alt="Successfull" src="https://github.com/user-attachments/assets/e20a85a6-7747-406c-8e05-b0c001a4f73b" />
<img width="1821" height="811" alt="Not_an_error_imput" src="https://github.com/user-attachments/assets/460620cc-4c7f-412c-af8d-d355f644d603" />
<img width="1827" height="798" alt="Fixed_output" src="https://github.com/user-attachments/assets/0cfbaa1d-2a38-4767-b904-828f074a6c35" />
<img width="1836" height="432" alt="Different_language_input" src="https://github.com/user-attachments/assets/8c8f61ee-2052-4fe2-9436-cff4f9a8fada" />




📜 License
MIT — free to use, modify, and share.
