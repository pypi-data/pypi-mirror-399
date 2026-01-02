"""OpenCV-based layout analysis for PDFs (used when confidence is low)."""

from pathlib import Path
from typing import TYPE_CHECKING, Dict, Optional, Any

if TYPE_CHECKING:
    import numpy as np

try:
    import cv2
    import numpy as np
except ImportError:
    cv2 = None
    np = None

try:
    import fitz  # PyMuPDF for PDF to image conversion
except ImportError:
    fitz = None


def analyze_with_opencv(file_path: str, page_num: int = 0) -> Optional[Dict[str, any]]:
    """
    Analyze PDF page layout using OpenCV for text/image region detection.
    
    This is used when initial heuristics have low confidence, to refine the decision.
    
    Args:
        file_path: Path to the PDF file
        page_num: Page number to analyze (0-indexed)
        
    Returns:
        Dictionary with layout analysis results:
            - text_regions: Number of detected text regions
            - image_regions: Number of detected image regions
            - text_coverage: Estimated text coverage percentage
            - image_coverage: Estimated image coverage percentage
            - layout_complexity: "simple", "moderate", or "complex"
            - has_text_regions: Boolean indicating text regions found
            - has_image_regions: Boolean indicating image regions found
        Returns None if OpenCV/PyMuPDF not available or analysis fails
    """
    if not cv2 or not np or not fitz:
        return None
    
    try:
        # Convert PDF page to image
        doc = fitz.open(file_path)
        if page_num >= len(doc):
            doc.close()
            return None
        
        page = doc[page_num]
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better quality
        img_array = np.frombuffer(pix.samples, dtype=np.uint8)
        if pix.n == 1:  # Grayscale
            img = img_array.reshape(pix.height, pix.width)
        else:
            img = img_array.reshape(pix.height, pix.width, pix.n)
        
        # Convert to grayscale if needed
        if len(img.shape) == 3:
            if img.shape[2] == 4:  # RGBA
                img = cv2.cvtColor(img, cv2.COLOR_RGBA2GRAY)
            elif img.shape[2] == 3:  # RGB
                img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        
        doc.close()
        
        # Analyze layout
        return _analyze_layout(img)
        
    except Exception:
        return None


def _analyze_layout(img: Any) -> Dict[str, any]:
    """
    Analyze image layout using OpenCV.
    
    Args:
        img: Grayscale image as numpy array
        
    Returns:
        Dictionary with layout analysis results
    """
    height, width = img.shape
    total_area = height * width
    
    # 1. Detect text regions using morphological operations
    # Text typically has high contrast and regular patterns
    _, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Morphological operations to connect text components
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    dilated = cv2.dilate(binary, kernel, iterations=2)
    
    # Find text contours
    text_contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter text regions (remove very small noise)
    text_regions = []
    text_area = 0
    for contour in text_contours:
        area = cv2.contourArea(contour)
        if area > 50:  # Minimum area threshold
            text_regions.append(contour)
            text_area += area
    
    # 2. Detect image regions using edge detection
    # Images typically have more edges and variation
    edges = cv2.Canny(img, 50, 150)
    
    # Find image regions (areas with high edge density)
    kernel_large = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
    edges_dilated = cv2.dilate(edges, kernel_large, iterations=1)
    
    image_contours, _ = cv2.findContours(edges_dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter image regions
    image_regions = []
    image_area = 0
    for contour in image_contours:
        area = cv2.contourArea(contour)
        if area > 500:  # Minimum area for images
            # Check if this region overlaps significantly with text regions
            # If so, it's likely not a pure image region
            overlap = False
            for text_contour in text_regions:
                if _contours_overlap(contour, text_contour):
                    overlap = True
                    break
            
            if not overlap:
                image_regions.append(contour)
                image_area += area
    
    # Calculate coverage percentages
    text_coverage = (text_area / total_area * 100) if total_area > 0 else 0.0
    image_coverage = (image_area / total_area * 100) if total_area > 0 else 0.0
    
    # Determine layout complexity
    num_regions = len(text_regions) + len(image_regions)
    if num_regions < 5:
        complexity = "simple"
    elif num_regions < 15:
        complexity = "moderate"
    else:
        complexity = "complex"
    
    return {
        "text_regions": len(text_regions),
        "image_regions": len(image_regions),
        "text_coverage": round(text_coverage, 2),
        "image_coverage": round(image_coverage, 2),
        "layout_complexity": complexity,
        "has_text_regions": len(text_regions) > 0,
        "has_image_regions": len(image_regions) > 0,
    }


def _contours_overlap(contour1, contour2, overlap_threshold: float = 0.3) -> bool:
    """
    Check if two contours overlap significantly.
    
    Args:
        contour1: First contour
        contour2: Second contour
        overlap_threshold: Minimum overlap ratio to consider as overlapping
        
    Returns:
        True if contours overlap significantly
    """
    if not cv2:
        return False
    
    try:
        # Get bounding boxes
        x1, y1, w1, h1 = cv2.boundingRect(contour1)
        x2, y2, w2, h2 = cv2.boundingRect(contour2)
        
        # Calculate intersection
        x_overlap = max(0, min(x1 + w1, x2 + w2) - max(x1, x2))
        y_overlap = max(0, min(y1 + h1, y2 + h2) - max(y1, y2))
        overlap_area = x_overlap * y_overlap
        
        # Calculate union
        area1 = w1 * h1
        area2 = w2 * h2
        union_area = area1 + area2 - overlap_area
        
        # Check overlap ratio
        if union_area == 0:
            return False
        
        overlap_ratio = overlap_area / union_area
        return overlap_ratio >= overlap_threshold
    except Exception:
        return False

