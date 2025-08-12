# graph.py
"""
Agentic RAG graph runner.

Nodes are *agentic*: each node function (agent) can return:
  - updated state (dict)
  - optionally a 'next_node' string in returned tuple or set state['_next_node']
  - or {'stop': True} to finish early
  - Stops early if PatchGeneratorAgent returns a diagnostic-only response.
Behavior:
 - If any agent (primarily the patch generator) returns a dict:
     {"type":"diagnostic_only", "message":"..."}
   the runner will stop immediately and the pipeline will return a failed/diagnostic result.
 - No patch generation, no execution, and no temp files for vague input.

Runner follows 'next_node' if provided, otherwise uses the graph edge order.
"""

import sys, os, time
from typing import Dict, Any, List, Optional, Callable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from rag.retriever import get_retriever
from agents.retriever_agent import RetrieverAgent
from agents.root_cause_agent import RootCauseAgent
from agents.patch_generator_agent import PatchGeneratorAgent
from agents.execution_agent import ExecutionAgent
from agents.validator_agent import ValidatorAgent
from config import MAX_ATTEMPTS

# instantiate agents
retriever_agent = RetrieverAgent(get_retriever())
root_cause_agent = RootCauseAgent()
patch_generator_agent = PatchGeneratorAgent()
execution_agent = ExecutionAgent()
validator_agent = ValidatorAgent()


class AgenticGraph:
    def __init__(self):
        self.nodes: Dict[str, Callable[[Dict[str, Any]], Any]] = {}
        self.edges: Dict[str, List[str]] = {}
        self.entry: Optional[str] = None

    def add_node(self, name: str, fn: Callable[[Dict[str, Any]], Any]):
        self.nodes[name] = fn

    def add_edge(self, src: str, dst: str):
        self.edges.setdefault(src, []).append(dst)

    def set_entry_point(self, name: str):
        if name not in self.nodes:
            raise ValueError(f"Entry point '{name}' is not registered")
        self.entry = name

    def run_one_pass(self, init_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute nodes from entry. If any node returns a diagnostic_only dict,
        set state['diagnostic'] and stop immediately.
        """
        if not self.entry:
            raise ValueError("Entry point not set")
        state = init_state
        current = self.entry
        visited = set()

        while current is not None:
            agent_fn = self.nodes.get(current)
            if not callable(agent_fn):
                break

            result = agent_fn(state)

            # EARLY: If an agent explicitly returns diagnostic_only, stop immediately.
            if isinstance(result, dict) and result.get("type") == "diagnostic_only":
                state["diagnostic"] = result.get("message", "")
                # make validation reflect diagnostic outcome
                state["validation"] = {"success": False, "message": state["diagnostic"]}
                break

            # NORMAL: merge or interpret results (conservative merging)
            next_node = None
            if isinstance(result, tuple) and len(result) == 2:
                state, next_node = result
            elif isinstance(result, dict):
                # Merge only known safe keys to avoid overriding full state.
                for k in ("patch_text", "execution_result", "root_cause_summary", "_next_node", "next_node"):
                    if k in result:
                        state[k] = result[k]
                next_node = result.get("_next_node") or result.get("next_node")
            else:
                # assume the node mutated state in place
                state = state

            # respect explicit state-set next node
            if not next_node:
                next_node = state.get("_next_node")

            outgoing = self.edges.get(current, [])
            if not next_node and outgoing:
                next_node = outgoing[0]

            # loop prevention for immediate repeats
            visited_key = (current, next_node)
            if visited_key in visited:
                break
            visited.add(visited_key)

            current = next_node

        return state


# ---------- Node implementations ----------
def build_agentic_graph() -> AgenticGraph:
    g = AgenticGraph()

    def node_retrieve(state: Dict[str, Any]) -> Dict[str, Any]:
        query = state.get("query") or state.get("error_log", "")
        try:
            state["retrieved_docs"] = retriever_agent.run(query)
        except Exception as e:
            state.setdefault("execution_result", {})["retrieve_error"] = str(e)
            state["_next_node"] = "validate"
        return state

    def node_analyze(state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            res = root_cause_agent.run(state.get("error_log", ""), state.get("retrieved_docs", []))
            if isinstance(res, dict):
                if "next_node" in res:
                    state["_next_node"] = res["next_node"]
                state["root_cause_summary"] = res.get("summary") or res.get("root_cause_summary") or ""
            else:
                state["root_cause_summary"] = res
        except Exception as e:
            state.setdefault("execution_result", {})["analyze_error"] = str(e)
        return state

    def node_generate(state: Dict[str, Any]) -> Any:
        # IMPORTANT: return the raw agent response so run_one_pass() can early-detect diagnostic_only.
        try:
            res = patch_generator_agent.run(
                state.get("error_log", ""),
                state.get("root_cause_summary", ""),
                state.get("retrieved_docs", []),
                state.get("user_code_snippet"),
            )
            # return raw response (string or dict). run_one_pass will handle diagnostic dicts.
            return res
        except Exception as e:
            state.setdefault("execution_result", {})["generate_error"] = str(e)
            return state

    def node_execute(state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            patch = state.get("patch_text")
            if not patch or not isinstance(patch, str) or patch.strip() == "":
                state.setdefault("execution_result", {})["error"] = "No patch to execute."
                state["_next_node"] = "validate"
                return state
            out = execution_agent.run(patch)
            state["execution_result"] = out
            if isinstance(out, dict) and out.get("critical_failure"):
                state["_next_node"] = "retrieve"
        except Exception as e:
            state["execution_result"] = {"stderr": "", "error": str(e)}
        return state

    def node_validate(state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            success, message = validator_agent.run(state.get("execution_result", {}))
            state["validation"] = {"success": bool(success), "message": str(message)}
        except Exception as e:
            state["validation"] = {"success": False, "message": f"validator error: {e}"}
        return state

    # register nodes & edges
    g.add_node("retrieve", node_retrieve)
    g.add_node("analyze", node_analyze)
    g.add_node("generate", node_generate)
    g.add_node("execute", node_execute)
    g.add_node("validate", node_validate)

    g.add_edge("retrieve", "analyze")
    g.add_edge("analyze", "generate")
    g.add_edge("generate", "execute")
    g.add_edge("execute", "validate")

    g.set_entry_point("retrieve")
    return g


# ---------- Pipeline ----------
def debug_pipeline(error_log: str, user_code_snippet: Optional[str] = None, max_attempts: int = MAX_ATTEMPTS) -> Dict[str, Any]:
    state: Dict[str, Any] = {"error_log": error_log, "user_code_snippet": user_code_snippet}
    graph = build_agentic_graph()
    attempt = 0
    history: List[Dict[str, Any]] = []

    while attempt < max_attempts:
        attempt += 1
        state["attempt"] = attempt

        # Run a single agentic pass
        state = graph.run_one_pass(state)

        # --- CRITICAL: Check for diagnostic-only and return immediately ---
        if "diagnostic" in state:
            # Return a clear structure: failed + diagnostic_message + attempts=attempt
            return {
                "status": "failed",
                "reason": "diagnostic_only",
                "diagnostic_message": state.get("diagnostic"),
                "attempts": attempt,
                "history": history,
            }

        # Normal attempt snapshot appended AFTER diagnostic check
        history.append({
            "attempt": attempt,
            "root_cause_summary": state.get("root_cause_summary"),
            "patch_text": state.get("patch_text"),
            "execution_result": state.get("execution_result"),
            "validation": state.get("validation"),
        })

        if state.get("validation", {}).get("success"):
            return {
                "status": "fixed",
                "attempts": attempt,
                "final_patch": state.get("patch_text"),
                "execution_result": state.get("execution_result"),
                "root_cause_summary": state.get("root_cause_summary"),
                "history": history,
            }

        # prepare for next attempt
        er = state.get("execution_result", {}) or {}
        stderr = er.get("stderr", "") if isinstance(er, dict) else ""
        state["query"] = state.get("error_log", "") + "\n\nExecution stderr:\n" + (stderr or "")

        time.sleep(0.5)

    return {"status": "failed", "attempts": attempt, "history": history, "message": f"Max attempts ({max_attempts}) reached."}
