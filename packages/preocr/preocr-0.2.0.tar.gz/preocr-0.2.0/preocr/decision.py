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
    ReasonCode,
)
from .reason_codes import get_reason_description


def decide(signals: Dict[str, any]) -> Tuple[bool, str, float, str, str]:
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
            - reason_code: Structured reason code (e.g., "PDF_DIGITAL", "IMAGE_FILE")
    """
    mime = signals.get("mime", "")
    text_length = signals.get("text_length", 0)
    extension = signals.get("extension", "")
    is_binary = signals.get("is_binary", True)
    
    # Rule 1: Plain text formats - NO OCR
    if mime.startswith("text/"):
        return (
            False,
            get_reason_description(ReasonCode.TEXT_FILE),
            HIGH_CONFIDENCE,
            CATEGORY_STRUCTURED,
            ReasonCode.TEXT_FILE,
        )
    
    # Rule 2: Office documents with text - NO OCR
    if "officedocument" in mime or extension in ["docx", "pptx", "xlsx"]:
        if text_length >= MIN_OFFICE_TEXT_LENGTH:
            return (
                False,
                f"{get_reason_description(ReasonCode.OFFICE_WITH_TEXT)} ({text_length} chars)",
                HIGH_CONFIDENCE,
                CATEGORY_STRUCTURED,
                ReasonCode.OFFICE_WITH_TEXT,
            )
        else:
            return (
                True,
                f"{get_reason_description(ReasonCode.OFFICE_NO_TEXT)} ({text_length} chars)",
                MEDIUM_CONFIDENCE,
                CATEGORY_UNSTRUCTURED,
                ReasonCode.OFFICE_NO_TEXT,
            )
    
    # Rule 3: Images - YES OCR (always)
    if mime.startswith("image/"):
        return (
            True,
            get_reason_description(ReasonCode.IMAGE_FILE),
            HIGH_CONFIDENCE,
            CATEGORY_UNSTRUCTURED,
            ReasonCode.IMAGE_FILE,
        )
    
    # Rule 4: PDFs
    if mime == "application/pdf" or extension == "pdf":
        if text_length >= MIN_TEXT_LENGTH:
            return (
                False,
                f"{get_reason_description(ReasonCode.PDF_DIGITAL)} ({text_length} chars)",
                HIGH_CONFIDENCE,
                CATEGORY_STRUCTURED,
                ReasonCode.PDF_DIGITAL,
            )
        else:
            return (
                True,
                f"{get_reason_description(ReasonCode.PDF_SCANNED)} ({text_length} chars)",
                MEDIUM_CONFIDENCE,
                CATEGORY_UNSTRUCTURED,
                ReasonCode.PDF_SCANNED,
            )
    
    # Rule 5: JSON/XML - NO OCR
    if mime in ["application/json", "application/xml"] or extension in ["json", "xml"]:
        return (
            False,
            get_reason_description(ReasonCode.STRUCTURED_DATA),
            HIGH_CONFIDENCE,
            CATEGORY_STRUCTURED,
            ReasonCode.STRUCTURED_DATA,
        )
    
    # Rule 6: HTML - NO OCR (text can be extracted)
    if mime in ["text/html", "application/xhtml+xml"] or extension in ["html", "htm"]:
        if text_length >= MIN_TEXT_LENGTH:
            return (
                False,
                f"{get_reason_description(ReasonCode.HTML_WITH_TEXT)} ({text_length} chars)",
                HIGH_CONFIDENCE,
                CATEGORY_STRUCTURED,
                ReasonCode.HTML_WITH_TEXT,
            )
        else:
            return (
                True,
                get_reason_description(ReasonCode.HTML_MINIMAL),
                LOW_CONFIDENCE,
                CATEGORY_UNSTRUCTURED,
                ReasonCode.HTML_MINIMAL,
            )
    
    # Rule 7: Unknown binaries - YES OCR (conservative default)
    if is_binary:
        return (
            True,
            get_reason_description(ReasonCode.UNKNOWN_BINARY),
            LOW_CONFIDENCE,
            CATEGORY_UNSTRUCTURED,
            ReasonCode.UNKNOWN_BINARY,
        )
    
    # Fallback: default to needing OCR
    return (
        True,
        get_reason_description(ReasonCode.UNRECOGNIZED_TYPE),
        LOW_CONFIDENCE,
        CATEGORY_UNSTRUCTURED,
        ReasonCode.UNRECOGNIZED_TYPE,
    )

