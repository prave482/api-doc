# 📘 API Documentation RAG System

## 📌 Project Description
This project is a *Retrieval-Augmented Generation (RAG) system* that allows users to upload *API documentation PDFs* and interactively ask questions or generate *code snippets* (Python, JavaScript, curl) strictly based on the uploaded document.

The system retrieves relevant documentation sections and uses a *Groq-hosted LLM* to generate accurate, grounded responses.

---

## 🎯 Objectives
- Enable easy understanding of complex API documentation
- Generate integration-ready code snippets
- Reduce manual effort in reading long API documents
- Demonstrate RAG architecture using modern LLMs

---

## 🚀 Features
- Upload API documentation (PDF)
- Intelligent document chunking & retrieval
- Context-aware question answering
- Code generation:
  - Python
  - JavaScript
  - curl
- Source citation for answers
- Fast inference using Groq API
- Simple Streamlit-based UI

---


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