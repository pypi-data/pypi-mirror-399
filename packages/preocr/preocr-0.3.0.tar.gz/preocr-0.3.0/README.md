# 🔍 PreOCR

<div align="center">

**A fast, CPU-only library that intelligently detects whether files need OCR processing**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)
[![PyPI version](https://badge.fury.io/py/preocr.svg)](https://badge.fury.io/py/preocr)

*Save time and money by skipping OCR for files that are already machine-readable*

</div>

---

## 🎯 What is PreOCR?

PreOCR is a **universal document gatekeeper** that analyzes any file type and answers one simple question:

> **"Is this file already machine-readable, or do I need OCR?"**

Instead of running expensive OCR on everything, PreOCR uses intelligent analysis to determine if OCR is actually needed. Perfect for filtering documents before sending them to expensive OCR engines like MinerU, Tesseract, or cloud OCR services.

## ✨ Key Features

- ⚡ **Fast**: CPU-only, typically < 1 second per file
- 🎯 **Accurate**: 92-95% accuracy with hybrid pipeline
- 🧠 **Smart**: Adaptive pipeline - fast heuristics for clear cases, OpenCV refinement for edge cases
- 🔒 **Deterministic**: Same input → same output
- 🚫 **OCR-free**: Never performs OCR to detect OCR
- 📄 **Page-level**: Analyze PDFs page-by-page (v0.2.0+)
- 🏷️ **Reason codes**: Structured codes for programmatic handling
- 🎨 **Layout-aware**: Detects mixed content and layout structure (v0.3.0+)

## 🚀 Quick Start

```bash
pip install preocr
```

```python
from preocr import needs_ocr

# Simple usage
result = needs_ocr("document.pdf")

if result["needs_ocr"]:
    print(f"Needs OCR: {result['reason']}")
    # Run your OCR here (e.g., MinerU)
else:
    print(f"Already readable: {result['reason']}")
```

## 📊 How It Works

PreOCR uses a **hybrid adaptive pipeline**:

```
┌─────────────┐
│  Any File   │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  Heuristics     │ ← Fast text extraction + rules
│  (Fast Path)    │   (< 1 second)
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Confidence ≥0.9?│
└──────┬──────────┘
       │
   ┌───┴───┐
   │       │
   YES     NO
   │       │
   ▼       ▼
┌─────┐ ┌─────────────────┐
│Return│ │ OpenCV Layout   │ ← Only for edge cases
│Fast! │ │ Analysis        │   (1-2 seconds)
└─────┘ └────────┬────────┘
                 │
                 ▼
         ┌───────────────┐
         │ Refine Decision│
         │ (Better Accuracy)│
         └───────┬───────┘
                 │
                 ▼
            ┌────────┐
            │ Result │
            └────────┘
```

**Performance:**
- **90% of files**: Fast path (< 1 second) - heuristics only
- **10% of files**: Refined path (1-2 seconds) - heuristics + OpenCV
- **Overall accuracy**: 92-95% (vs 85-90% with heuristics alone)

## 📦 Installation

### Basic Installation

```bash
pip install preocr
```

### With OpenCV Refinement (Recommended)

For improved accuracy on edge cases:

```bash
pip install preocr[layout-refinement]
```

This installs OpenCV and NumPy for layout analysis. The pipeline automatically uses OpenCV when confidence is low, even if installed separately.

## 💻 Usage Examples

### Basic Detection

```python
from preocr import needs_ocr

result = needs_ocr("document.pdf")

print(f"Needs OCR: {result['needs_ocr']}")
print(f"Confidence: {result['confidence']:.2f}")
print(f"Reason: {result['reason']}")
print(f"Reason Code: {result['reason_code']}")
```

### Page-Level Analysis

```python
result = needs_ocr("mixed_document.pdf", page_level=True)

if result["reason_code"] == "PDF_MIXED":
    print(f"Mixed PDF: {result['pages_needing_ocr']} pages need OCR")
    
    for page in result["pages"]:
        if page["needs_ocr"]:
            print(f"  Page {page['page_number']}: {page['reason']}")
```

### Layout-Aware Detection

```python
result = needs_ocr("document.pdf", layout_aware=True)

if result.get("layout"):
    layout = result["layout"]
    print(f"Layout Type: {layout['layout_type']}")
    print(f"Text Coverage: {layout['text_coverage']}%")
    print(f"Image Coverage: {layout['image_coverage']}%")
    print(f"Is Mixed Content: {layout['is_mixed_content']}")
```

### Batch Processing

```python
from pathlib import Path
from preocr import needs_ocr

files = Path("documents").glob("*.pdf")
needs_ocr_count = 0
skipped_count = 0

for file_path in files:
    result = needs_ocr(file_path)
    if result["needs_ocr"]:
        needs_ocr_count += 1
        # Process with OCR
    else:
        skipped_count += 1
        # Use existing text

print(f"OCR needed: {needs_ocr_count}, Skipped: {skipped_count}")
```

### Integration with OCR Engines

```python
from preocr import needs_ocr
# from mineru import ocr  # or your OCR engine

def process_document(file_path):
    result = needs_ocr(file_path)
    
    if result["needs_ocr"]:
        # Only run expensive OCR if needed
        ocr_result = ocr(file_path)
        return ocr_result
    else:
        # File is already machine-readable
        return {"text": extract_text(file_path), "source": "native"}
```

## 📋 Supported File Types

| File Type | Detection | Accuracy |
|-----------|-----------|----------|
| **PDFs** | Digital vs Scanned | 90-95% |
| **Images** | PNG, JPG, TIFF, etc. | 100% |
| **Office Docs** | DOCX, PPTX, XLSX | 85-90% |
| **Text Files** | TXT, CSV, HTML | 99% |
| **Structured Data** | JSON, XML | 99% |
| **Unknown Binaries** | Conservative default | 50-60% |

## 🎯 Reason Codes

PreOCR provides structured reason codes for programmatic handling:

### No OCR Needed
- `TEXT_FILE` - Plain text file
- `OFFICE_WITH_TEXT` - Office document with sufficient text
- `PDF_DIGITAL` - Digital PDF with extractable text
- `STRUCTURED_DATA` - JSON/XML files
- `HTML_WITH_TEXT` - HTML with sufficient content

### OCR Needed
- `IMAGE_FILE` - Image file
- `OFFICE_NO_TEXT` - Office document with insufficient text
- `PDF_SCANNED` - PDF appears to be scanned
- `PDF_MIXED` - PDF with mixed digital and scanned pages
- `HTML_MINIMAL` - HTML with minimal content
- `UNKNOWN_BINARY` - Unknown binary file type

### Page-Level Codes
- `PDF_PAGE_DIGITAL` - Individual page has extractable text
- `PDF_PAGE_SCANNED` - Individual page appears scanned

**Example:**
```python
result = needs_ocr("document.pdf")
if result["reason_code"] == "PDF_MIXED":
    # Handle mixed PDF
    process_mixed_pdf(result)
elif result["reason_code"] == "PDF_SCANNED":
    # All pages need OCR
    run_full_ocr(result)
```

## 📈 Performance

| Scenario | Time | Accuracy |
|----------|------|----------|
| Clear cases (90%) | < 1s | 99% |
| Edge cases (10%) | 1-2s | 85-90% |
| **Overall** | **~1.1s** | **92-95%** |

## 🏗️ Architecture

```
File Input
    ↓
File Type Detection (MIME, extension)
    ↓
Text Extraction Probe (PDF, Office, Text)
    ↓
Visual/Binary Analysis (Images, entropy)
    ↓
Decision Engine (Rule-based logic)
    ↓
Confidence Check
    ├─ High (≥0.9) → Return
    └─ Low (<0.9) → OpenCV Layout Analysis → Refine → Return
```

## 🔧 API Reference

### `needs_ocr(file_path, page_level=False, layout_aware=False)`

Main API function that determines if a file needs OCR.

**Parameters:**
- `file_path` (str or Path): Path to the file to analyze
- `page_level` (bool): If `True`, return page-level analysis for PDFs (default: `False`)
- `layout_aware` (bool): If `True`, perform explicit layout analysis for PDFs (default: `False`)

**Returns:**
Dictionary with:
- `needs_ocr` (bool): Whether OCR is needed
- `file_type` (str): File type category
- `category` (str): "structured" or "unstructured"
- `confidence` (float): Confidence score (0.0-1.0)
- `reason_code` (str): Structured reason code
- `reason` (str): Human-readable reason
- `signals` (dict): All collected signals (for debugging)
- `pages` (list, optional): Page-level results
- `layout` (dict, optional): Layout analysis results

## 🧪 Development

```bash
# Clone repository
git clone https://github.com/yuvaraj3855/preocr.git
cd preocr

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=preocr --cov-report=html
```

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

### Recent Updates

**v0.3.0** - Hybrid Pipeline with OpenCV Refinement
- Adaptive pipeline: fast heuristics + OpenCV for edge cases
- Improved accuracy (92-95%)
- Layout-aware detection
- Automatic confidence-based refinement

**v0.2.0** - Page-Level Detection
- Page-by-page analysis for PDFs
- Structured reason codes
- Enhanced confidence scoring

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

Apache License 2.0 - see [LICENSE](LICENSE) file for details.

## 🔗 Links

- **GitHub**: [https://github.com/yuvaraj3855/preocr](https://github.com/yuvaraj3855/preocr)
- **PyPI**: [https://pypi.org/project/preocr](https://pypi.org/project/preocr)
- **Issues**: [https://github.com/yuvaraj3855/preocr/issues](https://github.com/yuvaraj3855/preocr/issues)

## ⭐ Why PreOCR?

**Before PreOCR:**
- ❌ Run OCR on everything → Expensive, slow
- ❌ Manual inspection → Time-consuming
- ❌ No automation → Not scalable

**With PreOCR:**
- ✅ Skip OCR for 50-70% of files → Save money
- ✅ Fast decisions (< 1 second) → Don't slow pipeline
- ✅ Automated → Scalable
- ✅ 92-95% accurate → Good enough for production

**Perfect for:**
- Document processing pipelines
- Cost optimization (skip expensive OCR)
- Batch document analysis
- Pre-filtering before OCR engines (MinerU, Tesseract, etc.)

---

<div align="center">

**Made with ❤️ for efficient document processing**

[⭐ Star on GitHub](https://github.com/yuvaraj3855/preocr) | [📖 Documentation](https://github.com/yuvaraj3855/preocr#readme) | [🐛 Report Issue](https://github.com/yuvaraj3855/preocr/issues)

</div>
