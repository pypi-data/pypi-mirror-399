"""Decision engine to determine if OCR is needed."""

from typing import Dict, Tuple

from .constants import (
    CATEGORY_STRUCTURED,
    CATEGORY_UNSTRUCTURED,
    HIGH_CONFIDENCE,
    LOW_CONFIDENCE,
    MEDIUM_CONFIDENCE,
    MIN_OFFICE_TEXT_LENGTH,
    MIN_TEXT_LENGTH,
)


def decide(signals: Dict[str, any]) -> Tuple[bool, str, float, str]:
    """
    Decide if a file needs OCR based on collected signals.
    
    Args:
        signals: Dictionary of signals from signals.collect_signals()
        
    Returns:
        Tuple of:
            - needs_ocr: Boolean indicating if OCR is needed
            - reason: Human-readable reason for the decision
            - confidence: Confidence score (0.0-1.0)
            - category: "structured" or "unstructured"
    """
    mime = signals.get("mime", "")
    text_length = signals.get("text_length", 0)
    extension = signals.get("extension", "")
    is_binary = signals.get("is_binary", True)
    
    # Rule 1: Plain text formats - NO OCR
    if mime.startswith("text/"):
        return (
            False,
            "text file with extractable content",
            HIGH_CONFIDENCE,
            CATEGORY_STRUCTURED,
        )
    
    # Rule 2: Office documents with text - NO OCR
    if "officedocument" in mime or extension in ["docx", "pptx", "xlsx"]:
        if text_length >= MIN_OFFICE_TEXT_LENGTH:
            return (
                False,
                f"office document with {text_length} characters of text",
                HIGH_CONFIDENCE,
                CATEGORY_STRUCTURED,
            )
        else:
            return (
                True,
                f"office document with insufficient text ({text_length} chars)",
                MEDIUM_CONFIDENCE,
                CATEGORY_UNSTRUCTURED,
            )
    
    # Rule 3: Images - YES OCR (always)
    if mime.startswith("image/"):
        return (
            True,
            "image file (no text extraction possible)",
            HIGH_CONFIDENCE,
            CATEGORY_UNSTRUCTURED,
        )
    
    # Rule 4: PDFs
    if mime == "application/pdf" or extension == "pdf":
        if text_length >= MIN_TEXT_LENGTH:
            return (
                False,
                f"digital PDF with {text_length} characters of extractable text",
                HIGH_CONFIDENCE,
                CATEGORY_STRUCTURED,
            )
        else:
            return (
                True,
                f"PDF without extractable text ({text_length} chars) - likely scanned",
                MEDIUM_CONFIDENCE,
                CATEGORY_UNSTRUCTURED,
            )
    
    # Rule 5: JSON/XML - NO OCR
    if mime in ["application/json", "application/xml"] or extension in ["json", "xml"]:
        return (
            False,
            "structured data file (JSON/XML)",
            HIGH_CONFIDENCE,
            CATEGORY_STRUCTURED,
        )
    
    # Rule 6: HTML - NO OCR (text can be extracted)
    if mime in ["text/html", "application/xhtml+xml"] or extension in ["html", "htm"]:
        if text_length >= MIN_TEXT_LENGTH:
            return (
                False,
                f"HTML file with {text_length} characters of text",
                HIGH_CONFIDENCE,
                CATEGORY_STRUCTURED,
            )
        else:
            return (
                True,
                "HTML file with minimal content",
                LOW_CONFIDENCE,
                CATEGORY_UNSTRUCTURED,
            )
    
    # Rule 7: Unknown binaries - YES OCR (conservative default)
    if is_binary:
        return (
            True,
            "unknown binary file type",
            LOW_CONFIDENCE,
            CATEGORY_UNSTRUCTURED,
        )
    
    # Fallback: default to needing OCR
    return (
        True,
        "unrecognized file type",
        LOW_CONFIDENCE,
        CATEGORY_UNSTRUCTURED,
    )

