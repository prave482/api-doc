# API Doc RAG

A Streamlit-based Retrieval-Augmented Generation (RAG) system for API documentation.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   streamlit run app.py
   ```

## Project Structure

- `app.py`: Main Streamlit application
- `rag/`: RAG system components
  - `loader.py`: Document loading and preprocessing
  - `chunker.py`: Text chunking utilities
  - `vectorstore.py`: Vector storage and retrieval
  - `prompts.py`: Prompt templates
  - `pipeline.py`: Main RAG pipeline
- `data/uploads/`: Directory for uploaded documents
- `requirements.txt`: Python dependencies
- `README.md`: This file