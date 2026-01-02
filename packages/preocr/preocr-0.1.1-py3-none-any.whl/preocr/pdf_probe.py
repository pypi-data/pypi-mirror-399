"""PDF text extraction probe."""

from pathlib import Path
from typing import Dict, Optional

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None


def extract_pdf_text(file_path: str) -> Dict[str, any]:
    """
    Extract text from PDF file.
    
    Tries pdfplumber first (better text extraction), falls back to PyMuPDF.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Dictionary with keys:
            - text_length: Number of characters in extracted text
            - text: Extracted text (may be truncated for large files)
            - page_count: Number of pages in PDF
            - method: Extraction method used ("pdfplumber" or "pymupdf")
    """
    path = Path(file_path)
    
    # Try pdfplumber first
    if pdfplumber:
        try:
            return _extract_with_pdfplumber(path)
        except Exception:
            pass
    
    # Fallback to PyMuPDF
    if fitz:
        try:
            return _extract_with_pymupdf(path)
        except Exception:
            pass
    
    # No extractors available or both failed
    return {
        "text_length": 0,
        "text": "",
        "page_count": 0,
        "method": None,
    }


def _extract_with_pdfplumber(path: Path) -> Dict[str, any]:
    """Extract text using pdfplumber."""
    text_parts = []
    page_count = 0
    
    with pdfplumber.open(path) as pdf:
        page_count = len(pdf.pages)
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    
    full_text = "\n".join(text_parts)
    
    return {
        "text_length": len(full_text),
        "text": full_text[:1000] if len(full_text) > 1000 else full_text,
        "page_count": page_count,
        "method": "pdfplumber",
    }


def _extract_with_pymupdf(path: Path) -> Dict[str, any]:
    """Extract text using PyMuPDF."""
    doc = fitz.open(path)
    text_parts = []
    page_count = len(doc)
    
    for page_num in range(page_count):
        page = doc[page_num]
        page_text = page.get_text()
        if page_text:
            text_parts.append(page_text)
    
    doc.close()
    full_text = "\n".join(text_parts)
    
    return {
        "text_length": len(full_text),
        "text": full_text[:1000] if len(full_text) > 1000 else full_text,
        "page_count": page_count,
        "method": "pymupdf",
    }

