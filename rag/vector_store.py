# rag/vector_store.py

import os
import math
import time
from typing import List, Optional

import numpy as np
from sentence_transformers import SentenceTransformer
import chromadb
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
from config import VECTOR_DB_PATH, EMBEDDING_MODEL, EMBEDDING_BATCH_SIZE

try:
    import torch
except ImportError:
    torch = None


def _get_device() -> str:
    if torch is not None and torch.cuda.is_available():
        return "cuda"
    return "cpu"


def _ensure_client(persist_dir: str) -> chromadb.Client:
    os.makedirs(persist_dir, exist_ok=True)
    client = chromadb.PersistentClient(path=persist_dir)
    print(f"Using chromadb.PersistentClient(path={persist_dir})")
    return client


def create_vector_store(
    documents: List[Document],
    collection_name: str = "autodoc",
    persist_directory: Optional[str] = None,
    batch_size: Optional[int] = None,
):
    if persist_directory is None:
        persist_directory = VECTOR_DB_PATH

    if not documents:
        raise ValueError("No documents provided to create_vector_store().")

    bs = int(batch_size or EMBEDDING_BATCH_SIZE or 32)
    device = _get_device()
    print(f"Embedding model: {EMBEDDING_MODEL}    device: {device}    batch_size: {bs}")

    model = SentenceTransformer(EMBEDDING_MODEL)
    try:
        model = model.to(device)
    except Exception:
        print("Warning: model.to(device) failed; continuing on CPU.")
        device = "cpu"

    texts = [d.page_content for d in documents]
    metadatas = [d.metadata if hasattr(d, "metadata") else {} for d in documents]
    ids = [str(i) for i in range(len(texts))]

    client = _ensure_client(persist_directory)

    try:
        collection = client.get_collection(collection_name)
        print(f"Collection '{collection_name}' exists — will upsert into it.")
    except Exception:
        collection = client.create_collection(collection_name)
        print(f"Created new collection '{collection_name}'")

    total = len(texts)
    n_batches = math.ceil(total / bs)
    print(f"Total chunks: {total}  — encoding in {n_batches} batches of up to {bs}")

    start_time = time.time()
    for i in range(n_batches):
        s = i * bs
        e = min(total, (i + 1) * bs)
        batch_texts = texts[s:e]
        batch_ids = ids[s:e]
        batch_meta = metadatas[s:e]

        embeddings = model.encode(
            batch_texts,
            batch_size=bs,
            show_progress_bar=False,
            convert_to_numpy=True,
        )
        if not isinstance(embeddings, np.ndarray):
            embeddings = np.array(embeddings)
        emb_list = embeddings.tolist()

        collection.add(
            ids=batch_ids,
            documents=batch_texts,
            metadatas=batch_meta,
            embeddings=emb_list,
        )

        if (i + 1) % 5 == 0 or i == n_batches - 1:
            elapsed = time.time() - start_time
            print(f"  Batch {i+1}/{n_batches} inserted (items {s}:{e}). elapsed: {elapsed:.1f}s")

    total_time = time.time() - start_time
    print(f"✅ Done. Indexed {total} chunks into collection '{collection_name}' in {total_time:.1f}s")

    return client.get_collection(collection_name)


def load_vector_store(collection_name: str = "autodoc", persist_directory: Optional[str] = None):
    """
    Low-level function: returns chromadb.Collection object.
    """
    persist_directory = persist_directory or VECTOR_DB_PATH
    client = _ensure_client(persist_directory)
    return client.get_collection(collection_name)

def load_langchain_vectorstore(collection_name: str = "autodoc", persist_directory: Optional[str] = None):
    """
    Returns a LangChain Chroma vector store wrapping the persistent Chroma client and collection.
    This allows use of `.as_retriever()` and other LangChain features.
    """
    persist_directory = persist_directory or VECTOR_DB_PATH
    client = _ensure_client(persist_directory)

    # Use LangChain embedding wrapper matching your embedding model
    # Change this if you used a different embedding model
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    vectordb = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        client=client,
    )
    return vectordb
