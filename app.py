import streamlit as st
from rag.loader import load_pdf
from rag.chunker import chunk_document
from rag.vectorstore import VectorStore
from rag.pipeline import RagPipeline

# ---------------------------
# Session State Initialization
# ---------------------------
if "vector_store" not in st.session_state:
    st.session_state.vector_store = VectorStore()

if "pipeline" not in st.session_state:
    st.session_state.pipeline = None

if "last_result" not in st.session_state:
    st.session_state.last_result = None

# ---------------------------
# Sidebar - Document Upload
# ---------------------------
with st.sidebar:
    st.header("Document Upload")
    uploaded_file = st.file_uploader(
        "Upload API Documentation (PDF)", type="pdf"
    )

    if uploaded_file:
        with st.spinner("Processing document..."):
            pages = load_pdf(uploaded_file, uploaded_file.name)
            chunks = chunk_document(pages)
            st.session_state.vector_store.add_chunks(chunks)
            st.session_state.pipeline = RagPipeline(
                st.session_state.vector_store
            )

        st.success("Document indexed successfully")

# ---------------------------
# Main UI
# ---------------------------
st.title("API Doc RAG")
st.write(
    "Ask questions about your uploaded API documentation or generate integration code."
)

question = st.text_input("Enter your question:")

# ✅ SEARCH / EXPLAIN BUTTON (NEW)
if st.button("Search / Explain"):
    if st.session_state.pipeline is None:
        st.error("Please upload an API document first.")
    elif not question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Generating response..."):
            st.session_state.last_result = (
                st.session_state.pipeline.run(f"Explain: {question}")
            )

# ---------------------------
# Action Buttons
# ---------------------------
col1, col2, col3 = st.columns(3)

def run_query(prefix):
    if st.session_state.pipeline is None:
        st.error("Please upload an API document first.")
        return

    if not question.strip():
        st.warning("Please enter a question.")
        return

    with st.spinner("Generating response..."):
        st.session_state.last_result = (
            st.session_state.pipeline.run(f"{prefix}: {question}")
        )

with col1:
    if st.button("Generate Python Code"):
        run_query("Generate Python code")

with col2:
    if st.button("Generate JavaScript Code"):
        run_query("Generate JavaScript code")

with col3:
    if st.button("Generate curl Command"):
        run_query("Generate curl command")

# ---------------------------
# Render Output (After Rerun)
# ---------------------------
if st.session_state.last_result:
    result = st.session_state.last_result

    st.markdown("---")
    st.subheader("Result")

    if result.get("explanation"):
        st.subheader("Explanation")
        st.write(result["explanation"])

    if result.get("code_snippet"):
        st.subheader("Code Snippet")

        if "python" in question.lower():
            lang = "python"
        elif "javascript" in question.lower() or "js" in question.lower():
            lang = "javascript"
        elif "curl" in question.lower():
            lang = "bash"
        else:
            lang = "text"

        st.code(result["code_snippet"], language=lang)

    if result.get("source_citations"):
        st.subheader("Source Citations")
        for citation in result["source_citations"]:
            st.write(f"- {citation}")
