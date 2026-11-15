import os
from typing import List, Dict, Any, Tuple
from pypdf import PdfReader

def extract_text_from_pdf(file_path: str) -> Tuple[List[Dict[str, Any]], int]:
    """
    Extracts text from a PDF file page by page using pypdf.
    
    Returns:
        tuple: (pages_data, total_pages)
        pages_data is a list of dicts: [{"page": page_number, "text": text_content}]
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found at: {file_path}")

    pages_data = []
    try:
        reader = PdfReader(file_path)
        total_pages = len(reader.pages)

        for page_index, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            # Clean up whitespace and form feeds
            cleaned_text = "\n".join(line.strip() for line in text.splitlines() if line.strip())
            if cleaned_text:
                pages_data.append({
                    "page": page_index + 1,  # 1-indexed page number
                    "text": cleaned_text
                })

        return pages_data, total_pages
    except Exception as e:
        raise RuntimeError(f"Failed to extract text from PDF: {str(e)}")

