# RAG pipeline module
# Orchestrates the retrieval-augmented generation process

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

from .prompts import (
    EXPLAIN_ENDPOINT_PROMPT,
    GENERATE_PYTHON_CODE_PROMPT,
    GENERATE_JAVASCRIPT_CODE_PROMPT,
    GENERATE_CURL_COMMAND_PROMPT
)


class RagPipeline:
    def __init__(self, vector_store):
        self.vector_store = vector_store
        self.client = Groq()  # Reads GROQ_API_KEY from environment

    def run(self, query):
        query_lower = query.lower()

        # ---------------------------
        # Select prompt type
        # ---------------------------
        if 'python' in query_lower:
            prompt_template = GENERATE_PYTHON_CODE_PROMPT
            task_type = 'code'
        elif 'javascript' in query_lower or 'js' in query_lower or 'axios' in query_lower:
            prompt_template = GENERATE_JAVASCRIPT_CODE_PROMPT
            task_type = 'code'
        elif 'curl' in query_lower:
            prompt_template = GENERATE_CURL_COMMAND_PROMPT
            task_type = 'code'
        else:
            prompt_template = EXPLAIN_ENDPOINT_PROMPT
            task_type = 'explanation'

        # ---------------------------
        # Retrieve relevant chunks
        # ---------------------------
        retrieved = self.vector_store.retrieve(query, k=5)
        if not retrieved:
            return {
                "explanation": "Not found in provided documentation",
                "code_snippet": None,
                "source_citations": []
            }

        docs_text = "\n\n".join([
            f"Page {r['metadata']['page_number']}, "
            f"Section {r['metadata']['section_name']}:\n{r['text']}"
            for r in retrieved
        ])

        prompt = prompt_template.format(docs=docs_text, query=query)

        # ---------------------------
        # Groq API call (NON-LLAMA MODEL)
        # ---------------------------
        response = self.client.chat.completions.create(
            model="gemma-7b-it",
            messages=[
                {
                    "role": "system",
                    "content": "You are an API documentation assistant. Answer strictly using the provided documentation."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,
            max_tokens=1000
        )

        answer = response.choices[0].message.content.strip()

        # ---------------------------
        # Structure response
        # ---------------------------
        explanation = answer if task_type == "explanation" else None
        code_snippet = answer if task_type == "code" else None

        source_citations = [
            f"Page {r['metadata']['page_number']}, "
            f"Section {r['metadata']['section_name']}"
            for r in retrieved
        ]

        return {
            "explanation": explanation,
            "code_snippet": code_snippet,
            "source_citations": source_citations
        }
