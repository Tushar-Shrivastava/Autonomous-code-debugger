# Scripts/build_index.py
import sys
import os
from pathlib import Path

# ensure project root is on sys.path so `rag` package is importable
this_file = Path(__file__).resolve()
project_root = this_file.parent.parent  # two levels: Scripts/ -> project root
sys.path.insert(0, str(project_root))

from rag.document_loader import load_documents
from rag.vector_store import create_vector_store

if __name__ == "__main__":
    docs_dir = os.path.join(project_root, "data", "docs")
    print(f"Project root: {project_root}")
    print(f"Looking for documents in: {docs_dir}\n")

    if not os.path.isdir(docs_dir):
        print("❌ data/docs directory not found. Create the folder and add .pdf/.txt/.md files.")
        sys.exit(1)

    try:
        print("Loading documents ... (this may take a moment for PDFs)")
        docs = load_documents(docs_dir)
        print(f"\nTotal chunks returned by loader: {len(docs)}")
        if len(docs) == 0:
            print("❌ No chunks to index. Fix input documents and retry.")
            sys.exit(1)

        print("Building vector store ...")
        create_vector_store(docs)
        print("Done.")
    except KeyboardInterrupt:
        print("Interrupted by user.")
    except Exception as e:
        print(f"❌ Indexing failed with exception: {e}")
        raise
