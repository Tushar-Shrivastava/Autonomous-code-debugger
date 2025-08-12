import re
from langchain_anthropic import ChatAnthropic
from config import ANTHROPIC_API_KEY



class PatchGeneratorAgent:
    def __init__(self, model_name: str = "claude-sonnet-4-20250514", temperature: float = 0.5):
        self.llm = ChatAnthropic(
            model=model_name,
            temperature=temperature,
            anthropic_api_key=ANTHROPIC_API_KEY,
            max_retries=2
        )

    def _looks_like_valid_error(self, text: str) -> bool:
        """
        Check if the text contains patterns that look like a real Python error/traceback.
        """
        if not text or len(text.strip()) < 10:  # very short inputs
            return False

        patterns = [
            r"Traceback \(most recent call last\):",
            r"File \".*\", line \d+",
            r"(Error|Exception):"
        ]
        return any(re.search(p, text, re.IGNORECASE) for p in patterns)

    def run(self, error_log: str, root_cause_summary: str, retrieved_docs: list, user_code_snippet: str = None):
        # 1. If error log is too vague, return diagnostic-only response
        if not self._looks_like_valid_error(error_log):
            return {
                "type": "diagnostic_only",
                "message": (
                    "The provided input does not look like a valid Python error log or traceback.\n"
                    "Please provide the full Python error message (including any 'Traceback' lines) "
                    "and, if possible, the relevant code snippet."
                )
            }


        docs_text = "\n\n".join(retrieved_docs[:6]) if retrieved_docs else ""
        prompt = (
            "You are a careful Python coding assistant. Produce a **minimal** code patch or snippet to fix the issue.\n\n"
            f"Error log:\n{error_log}\n\n"
            f"Root cause analysis (short):\n{root_cause_summary}\n\n"
            f"Relevant docs:\n{docs_text}\n\n"
            f"User code (if provided):\n{user_code_snippet or 'None'}\n\n"
            "- If you are not confident the issue is in Python, respond exactly with:\n"
            "  I don't know - not a Python error.\n\n"
            "Return only fenced Python code blocks (```python ... ```).  or the exact phrase above if not a Python error."
        )
        resp = self.llm.predict(prompt)
        return {
            "type": "patch",
            "patch_text": resp.strip()
        }
