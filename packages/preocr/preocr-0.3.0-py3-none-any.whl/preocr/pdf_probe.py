"""PDF text extraction probe."""

from pathlib import Path
from typing import Dict, List, Optional

from .constants import MIN_TEXT_LENGTH

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None


def extract_pdf_text(file_path: str, page_level: bool = False) -> Dict[str, any]:
    """
    Extract text from PDF file.
    
    Tries pdfplumber first (better text extraction), falls back to PyMuPDF.
    
    Args:
        file_path: Path to the PDF file
        page_level: If True, return per-page analysis
        
    Returns:
        Dictionary with keys:
            - text_length: Number of characters in extracted text
            - text: Extracted text (may be truncated for large files)
            - page_count: Number of pages in PDF
            - method: Extraction method used ("pdfplumber" or "pymupdf")
            - pages: (if page_level=True) List of page-level results
    """
    path = Path(file_path)
    
    # Try pdfplumber first
    if pdfplumber:
        try:
            return _extract_with_pdfplumber(path, page_level)
        except Exception:
            pass
    
    # Fallback to PyMuPDF
    if fitz:
        try:
            return _extract_with_pymupdf(path, page_level)
        except Exception:
            pass
    
    # No extractors available or both failed
    result = {
        "text_length": 0,
        "text": "",
        "page_count": 0,
        "method": None,
    }
    if page_level:
        result["pages"] = []
    return result


def _extract_with_pdfplumber(path: Path, page_level: bool = False) -> Dict[str, any]:
    """Extract text using pdfplumber."""
    text_parts = []
    page_count = 0
    pages_data = []
    
    with pdfplumber.open(path) as pdf:
        page_count = len(pdf.pages)
        for page_num, page in enumerate(pdf.pages, start=1):
            page_text = page.extract_text() or ""
            text_parts.append(page_text)
            
            if page_level:
                page_text_len = len(page_text)
                pages_data.append({
                    "page_number": page_num,
                    "text_length": page_text_len,
                    "needs_ocr": page_text_len < MIN_TEXT_LENGTH,
                    "has_text": page_text_len > 0,
                })
    
    full_text = "\n".join(text_parts)
    
    result = {
        "text_length": len(full_text),
        "text": full_text[:1000] if len(full_text) > 1000 else full_text,
        "page_count": page_count,
        "method": "pdfplumber",
    }
    
    if page_level:
        result["pages"] = pages_data
    
    return result


def _extract_with_pymupdf(path: Path, page_level: bool = False) -> Dict[str, any]:
    """Extract text using PyMuPDF."""
    doc = fitz.open(path)
    text_parts = []
    page_count = len(doc)
    pages_data = []
    
    for page_num in range(page_count):
        page = doc[page_num]
        page_text = page.get_text() or ""
        text_parts.append(page_text)
        
        if page_level:
            page_text_len = len(page_text)
            pages_data.append({
                "page_number": page_num + 1,
                "text_length": page_text_len,
                "needs_ocr": page_text_len < MIN_TEXT_LENGTH,
                "has_text": page_text_len > 0,
            })
    
    doc.close()
    full_text = "\n".join(text_parts)
    
    result = {
        "text_length": len(full_text),
        "text": full_text[:1000] if len(full_text) > 1000 else full_text,
        "page_count": page_count,
        "method": "pymupdf",
    }
    
    if page_level:
        result["pages"] = pages_data
    
    return result

