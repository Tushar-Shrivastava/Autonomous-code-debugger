class ValidatorAgent:
    def run(self, execution_result: dict):
        rc = execution_result.get("returncode")
        if rc == 0:
            return True, "Return code 0 — likely fixed."
        stderr = execution_result.get("stderr") or ""
        return False, f"Non-zero return code ({rc}). stderr excerpt: {stderr[:1000]}"
