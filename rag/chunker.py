# Text chunking module
# Splits documents into manageable chunks for processing

import re


def chunk_document(pages):
    """
    Intelligently chunk API documentation text.

    Args:
        pages: List of dicts with 'page_number' and 'text' from loader

    Returns:
        List of chunks with 'text' and 'metadata' (page_number, section_name)
    """
    # Combine all page texts into one string with position tracking
    full_text = ""
    page_positions = []
    current_pos = 0
    for page in pages:
        text = page['text']
        full_text += text
        page_positions.append((current_pos, current_pos + len(text), page['page_number']))
        current_pos += len(text)

    # Define section patterns for API documentation
    section_patterns = {
        'endpoints': re.compile(r'(?i)(GET|POST|PUT|DELETE|PATCH)\s+(/\w+)+'),
        'parameters': re.compile(r'(?i)#+\s*parameters?'),
        'authentication': re.compile(r'(?i)#+\s*auth(?:entication)?'),
        'errors': re.compile(r'(?i)#+\s*error[s]?'),
    }

    # Find all section start positions
    sections = []
    for section_name, pattern in section_patterns.items():
        for match in pattern.finditer(full_text):
            sections.append((match.start(), section_name))
    sections.sort(key=lambda x: x[0])

    # Chunk the text with overlap
    chunk_size = 3200  # Approximate 800 tokens
    overlap = 600       # Approximate 150 tokens
    chunks = []
    start = 0

    while start < len(full_text):
        end = min(start + chunk_size, len(full_text))
        chunk_text = full_text[start:end]

        # Determine page number for this chunk
        page_num = None
        for pos_start, pos_end, p_num in page_positions:
            if pos_start <= start < pos_end:
                page_num = p_num
                break

        # Determine section name for this chunk
        section_name = None
        for sec_pos, sec_name in reversed(sections):
            if sec_pos <= start:
                section_name = sec_name
                break

        chunks.append({
            'text': chunk_text,
            'metadata': {
                'page_number': page_num,
                'section_name': section_name
            }
        })

        start += chunk_size - overlap
        if start >= end:
            break

    return chunks