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
    
    # Rule 4: PDFs (with optional layout-aware analysis)
    if mime == "application/pdf" or extension == "pdf":
        # Check if layout analysis is available
        layout_type = signals.get("layout_type")
        is_mixed_content = signals.get("is_mixed_content", False)
        text_coverage = signals.get("text_coverage", 0.0)
        image_coverage = signals.get("image_coverage", 0.0)
        has_images = signals.get("has_images", False)
        
        # Layout-aware decision (if layout analysis was performed)
        if layout_type and layout_type != "unknown":
            # Mixed content: has both text and images
            if is_mixed_content:
                # If text coverage is significant, might not need full OCR
                if text_length >= MIN_TEXT_LENGTH and text_coverage > 10:
                    return (
                        False,
                        f"{get_reason_description(ReasonCode.PDF_DIGITAL)} (mixed content, {text_length} chars, {text_coverage:.1f}% text coverage)",
                        MEDIUM_CONFIDENCE,
                        CATEGORY_STRUCTURED,
                        ReasonCode.PDF_DIGITAL,
                    )
                else:
                    # Mixed but text is sparse - needs OCR for images
                    return (
                        True,
                        f"{get_reason_description(ReasonCode.PDF_MIXED)} ({text_length} chars, {image_coverage:.1f}% images)",
                        MEDIUM_CONFIDENCE,
                        CATEGORY_UNSTRUCTURED,
                        ReasonCode.PDF_MIXED,
                    )
            
            # Image-only layout
            elif layout_type == "image_only":
                return (
                    True,
                    f"{get_reason_description(ReasonCode.PDF_SCANNED)} (image-only layout, {image_coverage:.1f}% images)",
                    HIGH_CONFIDENCE,
                    CATEGORY_UNSTRUCTURED,
                    ReasonCode.PDF_SCANNED,
                )
            
            # Text-only layout
            elif layout_type == "text_only":
                if text_length >= MIN_TEXT_LENGTH:
                    return (
                        False,
                        f"{get_reason_description(ReasonCode.PDF_DIGITAL)} (text-only layout, {text_length} chars)",
                        HIGH_CONFIDENCE,
                        CATEGORY_STRUCTURED,
                        ReasonCode.PDF_DIGITAL,
                    )
                else:
                    # Text-only but sparse - might be scanned text
                    return (
                        True,
                        f"{get_reason_description(ReasonCode.PDF_SCANNED)} (text-only layout but sparse, {text_length} chars)",
                        MEDIUM_CONFIDENCE,
                        CATEGORY_UNSTRUCTURED,
                        ReasonCode.PDF_SCANNED,
                    )
        
        # Fallback to text-length based decision (when layout analysis not available)
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


def refine_with_opencv(
    signals: Dict[str, any],
    opencv_result: Dict[str, any],
    initial_needs_ocr: bool,
    initial_reason: str,
    initial_confidence: float,
    initial_category: str,
    initial_reason_code: str,
) -> Tuple[bool, str, float, str, str]:
    """
    Refine decision using OpenCV layout analysis results.
    
    This is called when initial heuristics have low confidence (< 0.9).
    Uses OpenCV layout analysis to improve accuracy.
    
    Args:
        signals: Original signals from heuristics
        opencv_result: OpenCV layout analysis results
        initial_needs_ocr: Initial decision from heuristics
        initial_reason: Initial reason
        initial_confidence: Initial confidence score
        initial_category: Initial category
        initial_reason_code: Initial reason code
        
    Returns:
        Refined decision tuple: (needs_ocr, reason, confidence, category, reason_code)
    """
    text_length = signals.get("text_length", 0)
    text_coverage_opencv = opencv_result.get("text_coverage", 0.0)
    image_coverage_opencv = opencv_result.get("image_coverage", 0.0)
    has_text_regions = opencv_result.get("has_text_regions", False)
    has_image_regions = opencv_result.get("has_image_regions", False)
    layout_complexity = opencv_result.get("layout_complexity", "simple")
    
    # Refinement logic based on OpenCV analysis
    # If OpenCV detects text regions but heuristics found little text,
    # it might be scanned text that needs OCR
    if has_text_regions and text_length < MIN_TEXT_LENGTH:
        # Text regions detected but no extractable text = likely scanned
        if text_coverage_opencv > 10:
            return (
                True,
                f"{get_reason_description(ReasonCode.PDF_SCANNED)} (OpenCV detected text regions but no extractable text, {text_coverage_opencv:.1f}% coverage)",
                min(initial_confidence + 0.15, HIGH_CONFIDENCE),
                CATEGORY_UNSTRUCTURED,
                ReasonCode.PDF_SCANNED,
            )
    
    # If OpenCV detects significant text coverage, refine confidence upward
    if text_coverage_opencv > 15 and text_length >= MIN_TEXT_LENGTH:
        return (
            False,
            f"{get_reason_description(ReasonCode.PDF_DIGITAL)} (OpenCV confirmed text regions, {text_length} chars, {text_coverage_opencv:.1f}% coverage)",
            min(initial_confidence + 0.1, HIGH_CONFIDENCE),
            CATEGORY_STRUCTURED,
            ReasonCode.PDF_DIGITAL,
        )
    
    # If OpenCV detects image regions but no text, definitely needs OCR
    if has_image_regions and not has_text_regions and text_length < MIN_TEXT_LENGTH:
        return (
            True,
            f"{get_reason_description(ReasonCode.PDF_SCANNED)} (OpenCV detected image-only layout, {image_coverage_opencv:.1f}% images)",
            min(initial_confidence + 0.2, HIGH_CONFIDENCE),
            CATEGORY_UNSTRUCTURED,
            ReasonCode.PDF_SCANNED,
        )
    
    # Mixed content detected by OpenCV
    if has_text_regions and has_image_regions:
        if text_coverage_opencv > 10 and text_length >= MIN_TEXT_LENGTH:
            # Text is significant, might not need full OCR
            return (
                False,
                f"{get_reason_description(ReasonCode.PDF_DIGITAL)} (OpenCV detected mixed content, text sufficient, {text_length} chars)",
                min(initial_confidence + 0.1, MEDIUM_CONFIDENCE + 0.1),
                CATEGORY_STRUCTURED,
                ReasonCode.PDF_DIGITAL,
            )
        else:
            # Mixed but text is sparse, needs OCR
            return (
                True,
                f"{get_reason_description(ReasonCode.PDF_MIXED)} (OpenCV detected mixed content, {text_coverage_opencv:.1f}% text, {image_coverage_opencv:.1f}% images)",
                min(initial_confidence + 0.15, MEDIUM_CONFIDENCE + 0.1),
                CATEGORY_UNSTRUCTURED,
                ReasonCode.PDF_MIXED,
            )
    
    # If OpenCV confirms initial decision, increase confidence
    if (initial_needs_ocr and not has_text_regions) or (not initial_needs_ocr and has_text_regions):
        return (
            initial_needs_ocr,
            f"{initial_reason} (OpenCV confirmed)",
            min(initial_confidence + 0.1, HIGH_CONFIDENCE),
            initial_category,
            initial_reason_code,
        )
    
    # Default: return refined but keep initial decision
    return (
        initial_needs_ocr,
        f"{initial_reason} (OpenCV refined)",
        min(initial_confidence + 0.05, HIGH_CONFIDENCE),
        initial_category,
        initial_reason_code,
    )

