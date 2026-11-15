import os
from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter

def create_document_chunks(
    pages_data: List[Dict[str, Any]], 
    doc_id: str, 
    filename: str,
    chunk_size: int = 800,
    chunk_overlap: int = 150
) -> List[Dict[str, Any]]:
    """
    Splits page text into smaller contextual chunks while preserving page number and document metadata.
    
    Args:
        pages_data: List of dicts with 'page' and 'text'.
        doc_id: Unique identifier for the document.
        filename: Original file name of the PDF.
        chunk_size: Maximum characters per chunk.
        chunk_overlap: Overlap between consecutive chunks.
        
    Returns:
        List of dicts:
        [{
            "text": chunk_content,
            "metadata": {
                "chunk_id": f"{doc_id}_{page}_{idx}",
                "doc_id": doc_id,
                "filename": filename,
                "page": page_number,
                "chunk_index": idx
            }
        }]
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", "? ", "! ", " ", ""]
    )
    
    all_chunks: List[Dict[str, Any]] = []
    
    for page_info in pages_data:
        page_num = page_info["page"]
        raw_text = page_info["text"]
        
        split_texts = splitter.split_text(raw_text)
        for idx, text_segment in enumerate(split_texts):
            clean_segment = text_segment.strip()
            if len(clean_segment) > 15:  # filter out trivial noise
                all_chunks.append({
                    "text": clean_segment,
                    "metadata": {
                        "chunk_id": f"{doc_id}_p{page_num}_c{idx}",
                        "doc_id": doc_id,
                        "filename": filename,
                        "page": page_num,
                        "chunk_index": idx
                    }
                })
                
    return all_chunks

