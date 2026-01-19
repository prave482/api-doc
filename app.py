import streamlit as st
from groq import Groq
import os
from rag.loader import load_pdf, load_url
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

if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------------------
# Sidebar - Document Upload
# ---------------------------
with st.sidebar:
    st.header("Document Upload")
    uploaded_file = st.file_uploader(
        "Upload API Documentation (PDF)", type="pdf"
    )
    url_input = st.text_input("Or enter API Documentation URL")

    if uploaded_file or url_input:
        with st.spinner("Processing document..."):
            try:
                if uploaded_file:
                    pages = load_pdf(uploaded_file, uploaded_file.name)
                elif url_input:
                    pages = load_url(url_input)
                else:
                    st.error("Please provide a valid file or URL.")
                    st.stop()
                chunks = chunk_document(pages)
                st.session_state.vector_store.add_chunks(chunks)
                st.session_state.pipeline = RagPipeline(
                    st.session_state.vector_store
                )
                st.success("Document indexed successfully")
            except Exception as e:
                st.error(f"Error processing document: {str(e)}")

# ---------------------------
# Main UI
# ---------------------------
st.title("API Doc RAG")

tab1, tab2 = st.tabs(["Document Q&A", "General Chat"])

with tab1:
    st.write("Ask questions about your uploaded API documentation or generate integration code.")

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

with tab2:
    st.write("Chat about any API or software-related questions.")

    # Display chat messages
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    # Chat input
    if prompt := st.chat_input("Ask a question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        with st.spinner("Thinking..."):
            if st.session_state.pipeline:
                # Use RAG for doc-based answers if relevant
                result = st.session_state.pipeline.run(prompt)
                response = result.get("explanation") or result.get("code_snippet") or "No relevant information found in the documentation."
                if result.get("source_citations"):
                    response += "\n\n**Sources:**\n" + "\n".join(f"- {c}" for c in result["source_citations"])
            else:
                # General Q&A
                try:
                    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
                    chat_response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.7,
                        max_tokens=2000
                    )
                    response = chat_response.choices[0].message.content
                except Exception as e:
                    response = f"Sorry, I encountered an error: {str(e)}"

        st.session_state.messages.append({"role": "assistant", "content": response})
        st.chat_message("assistant").write(response)
