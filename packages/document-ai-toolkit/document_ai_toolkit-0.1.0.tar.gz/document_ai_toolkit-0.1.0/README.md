# Document AI Toolkit

Production-ready document processing toolkit with AI capabilities for text extraction, table detection, OCR, entity recognition, and document classification.

## Features

- **Multi-Format Support**: PDF, DOCX, HTML, Markdown, TXT, images, and more
- **Text Extraction**: Simple, layout-aware, and structured extraction modes
- **Table Detection**: Automatic table detection with cell-level extraction
- **OCR Integration**: Built-in OCR support with Tesseract, EasyOCR, PaddleOCR
- **Entity Extraction**: Named entity recognition (persons, organizations, dates, etc.)
- **Document Classification**: Automatic document type detection
- **Layout Analysis**: Detect headers, footers, paragraphs, lists, and more
- **Zero Dependencies Core**: Core functionality works without heavy dependencies

## Installation

```bash
pip install document-ai-toolkit          # Core
pip install document-ai-toolkit[pdf]     # PDF support
pip install document-ai-toolkit[ocr]     # OCR support
pip install document-ai-toolkit[full]    # All features
```

## Quick Start

```python
from document_ai_toolkit import DocumentProcessor, ProcessingConfig

# Basic processing
processor = DocumentProcessor()
result = processor.process("document.pdf")

print(result.document.content)
print(f"Pages: {result.document.metadata.page_count}")

# With tables
config = ProcessingConfig(extract_tables=True)
processor = DocumentProcessor(config)
result = processor.process("report.pdf")

for table in result.document.tables:
    print(table.to_dict())

# Classification
from document_ai_toolkit import DocumentClassifier
classifier = DocumentClassifier()
result = classifier.classify("document.pdf")
print(f"Type: {result.document_type.value} ({result.confidence:.0%})")

# Comparison
from document_ai_toolkit import DocumentComparator
comparator = DocumentComparator()
result = comparator.compare("v1.docx", "v2.docx")
print(f"Similarity: {result.similarity_score:.0%}")
```

## Supported Formats

| Format | Extension | Read | Write |
|--------|-----------|------|-------|
| PDF | .pdf | ✅ | ✅ |
| Word | .docx | ✅ | ✅ |
| HTML | .html | ✅ | ✅ |
| Markdown | .md | ✅ | ✅ |
| Plain Text | .txt | ✅ | ✅ |
| Images | .png, .jpg | ✅ | ❌ |

## License

MIT License - Pranay M
