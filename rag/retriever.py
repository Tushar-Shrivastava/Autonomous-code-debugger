from rag.vector_store import load_langchain_vectorstore
from config import TOP_K_RESULTS

def get_retriever():
    vectordb = load_langchain_vectorstore()
    retriever = vectordb.as_retriever(search_kwargs={"k": TOP_K_RESULTS})
    return retriever

