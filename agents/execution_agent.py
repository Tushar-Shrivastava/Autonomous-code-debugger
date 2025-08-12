import subprocess
import tempfile
import os
import shutil
import uuid
from config import EXECUTION_TIMEOUT, USE_DOCKER_SANDBOX, SANDBOX_DOCKER_IMAGE

class ExecutionAgent:
    def __init__(self, timeout: int = EXECUTION_TIMEOUT):
        self.timeout = timeout

    def _extract_code(self, text: str):
        # crude: return first fenced python block
        if "```" in text:
            parts = text.split("```")
            for i in range(1, len(parts), 2):
                block = parts[i]
                # remove optional "python" header
                if block.strip().startswith("python"):
                    block = block.split("\n", 1)[1] if "\n" in block else ""
                return block
        return text  # fallback: assume the whole text is runnable code

    def _run_local(self, file_path: str):
        try:
            r = subprocess.run(["python", file_path], capture_output=True, text=True, timeout=self.timeout)
            return {"stdout": r.stdout, "stderr": r.stderr, "returncode": r.returncode}
        except subprocess.TimeoutExpired as e:
            return {"stdout": "", "stderr": f"TIMEOUT: {e}", "returncode": -1}
        except Exception as e:
            return {"stdout": "", "stderr": f"EXEC ERROR: {e}", "returncode": -1}

    def _run_docker(self, file_path: str):
        try:
            tmpdir = tempfile.mkdtemp()
            shutil.copy(file_path, os.path.join(tmpdir, "runfile.py"))
            container_name = f"debug-sandbox-{uuid.uuid4().hex[:8]}"
            cmd = [
                "docker", "run", "--rm", "--name", container_name,
                "-v", f"{tmpdir}:/work",
                "-w", "/work",
                SANDBOX_DOCKER_IMAGE,
                "python", "runfile.py"
            ]
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=self.timeout + 10)
            shutil.rmtree(tmpdir, ignore_errors=True)
            return {"stdout": r.stdout, "stderr": r.stderr, "returncode": r.returncode}
        except Exception as e:
            return {"stdout": "", "stderr": f"DOCKER ERROR: {e}", "returncode": -1}

    def run(self, code_text: str):
        code = self._extract_code(code_text)
        f = tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w", encoding="utf-8")
        try:
            f.write(code)
            f.flush()
            f.close()
            if USE_DOCKER_SANDBOX:
                return self._run_docker(f.name)
            else:
                return self._run_local(f.name)
        finally:
            try:
                os.remove(f.name)
            except Exception:
                pass
