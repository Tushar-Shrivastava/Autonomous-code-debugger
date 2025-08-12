# rag/document_loader.py
import os
from typing import List
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from config import DOCS_PATH, CHUNK_SIZE, CHUNK_OVERLAP

def _list_files(path: str):
    for root, _, files in os.walk(path):
        for f in sorted(files):
            yield os.path.join(root, f)

def load_documents(path: str = None) -> List[Document]:
    """
    Load and split documents (txt, md, pdf). Skip files that raise errors but print diagnostics.
    Returns a list of LangChain Document chunks ready for embedding.
    """
    if path is None:
        path = DOCS_PATH

    if not os.path.exists(path):
        raise FileNotFoundError(f"Documents path does not exist: {path}")

    loaded_docs = []
    file_count = 0
    attempted_files = []

    for file_path in _list_files(path):
        file_count += 1
        attempted_files.append(file_path)
        basename = os.path.basename(file_path).lower()

        try:
            if basename.endswith((".txt", ".md", ".log")):
                # Text files — explicit encoding
                loader = TextLoader(file_path, encoding="utf-8")
                docs = loader.load()
                loaded_docs.extend(docs)
                print(f"Loaded text: {file_path} -> {len(docs)} document(s)")

            elif basename.endswith(".pdf"):
                # PDF files
                try:
                    loader = PyPDFLoader(file_path)
                    docs = loader.load()
                    loaded_docs.extend(docs)
                    print(f"Loaded PDF: {file_path} -> {len(docs)} page-doc(s)")
                except Exception as e_pdf:
                    # PDF parser failed; report and skip file (don't crash whole run)
                    print(f"⚠️ Error loading PDF {file_path}: {e_pdf}. Skipping this file.")
                    continue
            else:
                # skip unknown extensions but print
                print(f"Skipping unsupported file type: {file_path}")
                continue

        except Exception as exc:
            # catch-all per-file error
            print(f"⚠️ Error processing {file_path}: {repr(exc)}. Skipping.")
            continue

    print(f"\nTried to load {file_count} files. Successfully loaded {len(loaded_docs)} raw documents (pre-split).")
    if not loaded_docs:
        print("⚠️ Warning: No readable documents were loaded. Check your files/encodings and try again.")

    # Split into chunks
    if loaded_docs:
        splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
        split_docs = splitter.split_documents(loaded_docs)
        print(f"Split into {len(split_docs)} chunks (chunk_size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")
        return split_docs

    return []
