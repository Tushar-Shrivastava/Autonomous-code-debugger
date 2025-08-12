import os
from langchain_anthropic import ChatAnthropic
from config import ANTHROPIC_API_KEY



class RootCauseAgent:
    def __init__(self, model_name: str = "claude-sonnet-4-20250514", temperature: float = 0.5):
        self.llm = ChatAnthropic(
            model=model_name,
            temperature=temperature,
            anthropic_api_key=ANTHROPIC_API_KEY,
            max_retries=2
        )

    def run(self, error_log: str, retrieved_docs: list):
        docs_text = "\n\n".join(retrieved_docs[:6]) if retrieved_docs else "No docs found."
        prompt = (
            "You are an expert Python debugging assistant.\n\n"
            f"Error log:\n{error_log}\n\n"
            f"Retrieved docs (top results):\n{docs_text}\n\n"
            "1) Give 2-3 probable root causes (short). For each: reason and 1 diagnostic step.\n"
            "2) Recommend 1 preferred fix to attempt first (short).\n\n"
            "Return your response as plain text. If you are unsure or you think it is another language then python, say 'I don't know' and propose diagnostics."
        )
        resp = self.llm.predict(prompt)
        return resp
