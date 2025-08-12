class RetrieverAgent:
    def __init__(self, retriever):
        self.retriever = retriever

    def run(self, query: str):
        docs = self.retriever.get_relevant_documents(query)
        # return raw text content (page_content)
        return [d.page_content for d in docs]
