import streamlit as st
from graph import debug_pipeline

st.set_page_config(page_title="Agentic RAG Debugger", layout="wide")
st.title("🔧 Agentic RAG — Autonomous Code Debugger")

st.markdown("""
Paste an error log below (from Python, PyTorch, etc.).  
Optionally upload the failing `.py` file (or paste the snippet).  
The agent will:
1. Retrieve related docs from indexed PDFs/txts,
2. Propose a minimal patch,
3. Try to run it in a sandbox,
4. Validate and iterate up to MAX_ATTEMPTS.
""")

error_log = st.text_area("Error log (paste here)", height=250)
uploaded_file = st.file_uploader("Optional: upload failing .py file or log file", type=["py", "txt", "log"])
code_snippet = ""
if uploaded_file:
    try:
        code_snippet = uploaded_file.getvalue().decode("utf-8")
    except Exception:
        code_snippet = None

if st.button("Debug"):
    if not error_log.strip():
        st.error("Please paste an error log.")
    else:
        with st.spinner("Running agentic RAG debugger..."):
            res = debug_pipeline(error_log, user_code_snippet=code_snippet)
        st.write("Attempts:", res.get("attempts"))

        if res["status"] == "fixed":
            st.success(f"Finished: {res['status']}")
            st.subheader("Final Patch")
            st.code(res["final_patch"][:4000])
            st.subheader("Execution Output")
            st.json(res["execution_result"])
        else:
            # handle diagnostic-only specially
            if res.get("reason") == "diagnostic_only":
                st.error("Finished: failed — diagnostic only")
                st.subheader("Agent diagnostic")
                st.write(res.get("diagnostic_message"))
            else:
                st.error(f"Finished: {res['status']}")
                st.subheader("History of attempts")
                for attempt in res.get("history", []):
                    st.markdown(f"### Attempt {attempt['attempt']}")
                    st.write("Root cause summary (raw):")
                    st.text(attempt.get("root_cause_summary", "")[:2000])
                    st.write("Patch generated:")
                    st.code(attempt.get("patch_text", "")[:4000])
                    st.write("Execution result (short):")
                    er = attempt.get("execution_result", {})
                    st.json({"returncode": er.get("returncode"), "stderr": er.get("stderr", "")[:1000]})
        st.info("Remember: don't run untrusted patches on production systems. Use Docker sandbox for safety.")
