"""Main API for OCR detection."""

from pathlib import Path
from typing import Any, Dict, Union

from . import decision
from . import filetype
from . import image_probe
from . import office_probe
from . import pdf_probe
from . import signals
from . import text_probe


def needs_ocr(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Determine if a file needs OCR processing.
    
    This is the main API function. It analyzes the file type, extracts text
    where possible, and makes an intelligent decision about whether OCR is needed.
    
    Args:
        file_path: Path to the file to analyze (string or Path object)
        
    Returns:
        Dictionary with keys:
            - needs_ocr: Boolean indicating if OCR is needed
            - file_type: Detected file type category (e.g., "image", "pdf", "office")
            - category: "structured" (no OCR) or "unstructured" (needs OCR)
            - confidence: Confidence score (0.0-1.0)
            - reason: Human-readable reason for the decision
            - signals: Dictionary of all collected signals (for debugging)
            
    Example:
        >>> result = needs_ocr("document.pdf")
        >>> if result["needs_ocr"]:
        ...     run_ocr("document.pdf")
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Step 1: Detect file type
    file_info = filetype.detect_file_type(str(path))
    mime = file_info["mime"]
    
    # Step 2: Extract text based on file type
    text_result = None
    image_result = None
    
    if mime == "application/pdf":
        # PDF text extraction
        text_result = pdf_probe.extract_pdf_text(str(path))
    elif "officedocument" in mime or file_info["extension"] in ["docx", "pptx", "xlsx"]:
        # Office document text extraction
        text_result = office_probe.extract_office_text(str(path), mime)
    elif mime.startswith("text/") or mime in ["text/html", "application/xhtml+xml"]:
        # Plain text or HTML extraction
        text_result = text_probe.extract_text_from_file(str(path), mime)
    elif mime.startswith("image/"):
        # Image analysis (no text extraction)
        image_result = image_probe.analyze_image(str(path))
    
    # Step 3: Collect all signals
    collected_signals = signals.collect_signals(
        str(path), file_info, text_result, image_result
    )
    
    # Step 4: Make decision
    needs_ocr_flag, reason, confidence, category = decision.decide(collected_signals)
    
    # Step 5: Determine file type category for user
    file_type_category = _get_file_type_category(mime, file_info["extension"])
    
    return {
        "needs_ocr": needs_ocr_flag,
        "file_type": file_type_category,
        "category": category,
        "confidence": confidence,
        "reason": reason,
        "signals": collected_signals,
    }


def _get_file_type_category(mime: str, extension: str) -> str:
    """Get a user-friendly file type category."""
    if mime.startswith("image/"):
        return "image"
    elif mime == "application/pdf" or extension == "pdf":
        return "pdf"
    elif "officedocument" in mime or extension in ["docx", "pptx", "xlsx", "doc", "ppt", "xls"]:
        return "office"
    elif mime.startswith("text/") or extension in ["txt", "csv", "html", "htm"]:
        return "text"
    elif mime in ["application/json", "application/xml"] or extension in ["json", "xml"]:
        return "structured"
    else:
        return "unknown"

