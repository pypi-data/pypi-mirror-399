"""Main API for OCR detection."""

from pathlib import Path
from typing import Any, Dict, Optional, Union

from . import decision
from . import filetype
from . import image_probe
from . import layout_analyzer
from . import office_probe
from . import opencv_layout
from . import page_detection
from . import pdf_probe
from . import signals
from . import text_probe
from .constants import LAYOUT_REFINEMENT_THRESHOLD


def needs_ocr(
    file_path: Union[str, Path],
    page_level: bool = False,
    layout_aware: bool = False,
) -> Dict[str, Any]:
    """
    Determine if a file needs OCR processing.
    
    This is the main API function. It analyzes the file type, extracts text
    where possible, and makes an intelligent decision about whether OCR is needed.
    
    Args:
        file_path: Path to the file to analyze (string or Path object)
        page_level: If True, return page-level analysis for PDFs (default: False)
        layout_aware: If True, perform layout analysis for PDFs to detect mixed
                     content and improve accuracy (default: False)
        
    Returns:
        Dictionary with keys:
            - needs_ocr: Boolean indicating if OCR is needed
            - file_type: Detected file type category (e.g., "image", "pdf", "office")
            - category: "structured" (no OCR) or "unstructured" (needs OCR)
            - confidence: Confidence score (0.0-1.0)
            - reason: Human-readable reason for the decision
            - reason_code: Structured reason code (e.g., "PDF_DIGITAL", "IMAGE_FILE")
            - signals: Dictionary of all collected signals (for debugging)
            - pages: (if page_level=True for PDFs) Page-level analysis results
            - layout: (if layout_aware=True for PDFs) Layout analysis results
            
    Example:
        >>> result = needs_ocr("document.pdf")
        >>> if result["needs_ocr"]:
        ...     run_ocr("document.pdf")
        
        >>> # Page-level analysis
        >>> result = needs_ocr("document.pdf", page_level=True)
        >>> for page in result.get("pages", []):
        ...     if page["needs_ocr"]:
        ...         print(f"Page {page['page_number']} needs OCR")
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
    page_analysis = None
    layout_result = None
    
    if mime == "application/pdf":
        # PDF text extraction (with optional page-level analysis)
        text_result = pdf_probe.extract_pdf_text(str(path), page_level=page_level)
        
        # Perform layout analysis if requested
        if layout_aware:
            layout_result = layout_analyzer.analyze_pdf_layout(
                str(path), page_level=page_level
            )
        
        # Perform page-level analysis if requested
        if page_level and "pages" in text_result:
            page_analysis = page_detection.analyze_pdf_pages(
                str(path), file_info, text_result
            )
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
        str(path), file_info, text_result, image_result, layout_result
    )
    
    # Step 4: Make initial decision (heuristics)
    needs_ocr_flag, reason, confidence, category, reason_code = decision.decide(collected_signals)
    
    # Step 5: Confidence check → OpenCV layout refinement (if needed)
    # If confidence is low, use OpenCV to refine the decision
    if mime == "application/pdf" and confidence < LAYOUT_REFINEMENT_THRESHOLD:
        opencv_result = opencv_layout.analyze_with_opencv(str(path), page_num=0)
        if opencv_result:
            # Refine decision based on OpenCV analysis
            needs_ocr_flag, reason, confidence, category, reason_code = decision.refine_with_opencv(
                collected_signals, opencv_result, needs_ocr_flag, reason, confidence, category, reason_code
            )
            # Add OpenCV results to signals for debugging
            collected_signals["opencv_layout"] = opencv_result
    
    # Step 6: Determine file type category for user
    file_type_category = _get_file_type_category(mime, file_info["extension"])
    
    # Build result dictionary
    result = {
        "needs_ocr": needs_ocr_flag,
        "file_type": file_type_category,
        "category": category,
        "confidence": confidence,
        "reason": reason,
        "reason_code": reason_code,
        "signals": collected_signals,
    }
    
    # Add page-level results if available
    if page_analysis and "pages" in page_analysis:
        result["pages"] = page_analysis.get("pages", [])
        result["page_count"] = page_analysis.get("page_count", 0)
        result["pages_needing_ocr"] = page_analysis.get("pages_needing_ocr", 0)
        result["pages_with_text"] = page_analysis.get("pages_with_text", 0)
        # Override overall decision with page-level analysis if available
        if page_analysis.get("overall_needs_ocr") is not None:
            result["needs_ocr"] = page_analysis["overall_needs_ocr"]
            result["confidence"] = page_analysis["overall_confidence"]
            result["reason_code"] = page_analysis["overall_reason_code"]
            result["reason"] = page_analysis["overall_reason"]
    
    # Add layout analysis results if available
    if layout_result:
        result["layout"] = {
            "text_coverage": layout_result.get("text_coverage", 0.0),
            "image_coverage": layout_result.get("image_coverage", 0.0),
            "has_images": layout_result.get("has_images", False),
            "text_density": layout_result.get("text_density", 0.0),
            "layout_type": layout_result.get("layout_type", "unknown"),
            "is_mixed_content": layout_result.get("is_mixed_content", False),
        }
        if page_level and "pages" in layout_result:
            result["layout"]["pages"] = layout_result["pages"]
    
    return result


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

