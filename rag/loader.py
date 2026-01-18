# Data loader module
# Handles loading and preprocessing of API documentation

import os
import httpx
from pypdf import PdfReader


def load_pdf(uploaded_file, filename):
    """
    Load and extract text from an uploaded PDF file.

    Args:
        uploaded_file: Streamlit uploaded file object
        filename: Name to save the file as

    Returns:
        List of dicts with 'page_number' and 'text' for each page
    """
    # Create uploads directory if it doesn't exist
    upload_dir = "data/uploads"
    os.makedirs(upload_dir, exist_ok=True)

    # Save the uploaded file
    filepath = os.path.join(upload_dir, filename)
    with open(filepath, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Extract text from each page
    reader = PdfReader(filepath)
    pages = []
    for page_num, page in enumerate(reader.pages):
        text = page.extract_text()
        pages.append({
            "page_number": page_num + 1,
            "text": text
        })

    return pages


def load_url(url):
    """
    Load and extract text from a URL.

    Args:
        url: The URL to fetch content from

    Returns:
        List of dicts with 'page_number' and 'text'
    """
    response = httpx.get(url, timeout=30.0)
    response.raise_for_status()
    content = response.text
    # For simplicity, treat the entire content as one page
    return [{"page_number": 1, "text": content}]