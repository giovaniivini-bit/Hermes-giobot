---
name: ocr-tools
description: "OCR tools for document text extraction and image-to-spreadsheet conversion."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [OCR, Text-Extraction, PDF, Image, Spreadsheet]
    related_skills: [nano-pdf, powerpoint]
---

# OCR Tools

This skill provides tools for Optical Character Recognition (OCR) tasks, including extracting text from PDFs and scanned documents, and extracting text from images to create spreadsheets.

## Document OCR (ocr-and-documents)

Extract text from PDFs and scanned documents using `pymupdf` (lightweight) or `marker-pdf` (high-quality OCR with support for equations, tables, and multiple languages). See `references/ocr-and-documents.md` for full details.

## Image to Spreadsheet (ocr-planilha)

Extract text from images (particularly financial data in Brazilian Reais format) and create spreadsheets in Google Drive using OCR.space API and Google Sheets API. See `references/ocr-planilha.md` for full details.

## Vision Model Fallback

When `vision_analyze` or `browser_vision` fail with "No LLM provider configured for task=vision", use OCR.space API as a zero-dependency fallback to extract text from images:

```python
import json, base64, urllib.request, urllib.parse
from PIL import Image
import io

img = Image.open('/path/to/image.jpg')
buffer = io.BytesIO()
img.save(buffer, format='PNG')
b64 = base64.b64encode(buffer.getvalue()).decode()

data = urllib.parse.urlencode({
    'base64Image': 'data:image/png;base64,' + b64,
    'language': 'por',       # Portuguese; omit for English default
    'isOverlayRequired': 'false',
    'OCREngine': '2'
}).encode()

req = urllib.request.Request('https://api.ocr.space/parse/image', data=data)
req.add_header('Content-Type', 'application/x-www-form-urlencoded')
req.add_header('apikey', 'helloworld')  # Free tier key (500 req/day)

resp = urllib.request.urlopen(req, timeout=30)
result = json.loads(resp.read().decode())
text = result.get('ParsedResults', [{}])[0].get('ParsedText', '')
print(text)
```

Install deps once: `uv pip install pytesseract Pillow` (Pillow for image handling; pytesseract is optional — only if a local tesseract binary is available).

## Usage

Refer to the referenced documents for detailed usage instructions, scripts, and examples.

## References

- `references/ocr-and-documents.md`: Detailed guide for document OCR
- `references/ocr-planilha.md`: Detailed guide for image-to-spreadsheet OCR
- `references/ocr-lookup-sheet.md`: OCR → spreadsheet lookup (extract ref numbers from image, search sheet, report results)

## Scripts

- `scripts/extract_marker.py`: Helper script for marker-pdf based extraction (from ocr-and-documents)
- `scripts/extract_pymupdf.py`: Helper script for pymupdf based extraction (from ocr-and-documents)
- `scripts/process_images_to_sheet.py`: Helper script for processing images to Google Sheets (from ocr-planilha)