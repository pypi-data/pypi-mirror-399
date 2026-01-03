"""Document AI Toolkit - Comprehensive document processing for AI applications.

A production-ready toolkit for extracting, analyzing, and transforming
documents for AI/ML pipelines.

Example:
    >>> from document_ai_toolkit import DocumentProcessor
    >>> processor = DocumentProcessor()
    >>> result = processor.process("document.html")
    >>> print(result.text[:100])
    >>> print(f"Found {len(result.tables)} tables")
"""

from .types import (
    # Enums
    DocumentType,
    ElementType,
    ExtractionMethod,
    TableFormat,
    LayoutType,
    # Data classes
    BoundingBox,
    DocumentElement,
    TableCell,
    Table,
    PageInfo,
    DocumentMetadata,
    ExtractedImage,
    Entity,
    Section,
    ExtractionResult,
    ProcessingConfig,
    ClassificationResult,
    ComparisonResult,
)

from .processor import (
    # Main processor
    DocumentProcessor,
    # Extractors
    BaseExtractor,
    TextExtractor,
    HTMLExtractor,
    # Utilities
    TableExtractor,
    EntityExtractor,
    DocumentChunker,
    DocumentConverter,
)

__version__ = "0.1.0"
__author__ = "Pranay M"
__all__ = [
    # Enums
    "DocumentType",
    "ElementType",
    "ExtractionMethod",
    "TableFormat",
    "LayoutType",
    # Data classes
    "BoundingBox",
    "DocumentElement",
    "TableCell",
    "Table",
    "PageInfo",
    "DocumentMetadata",
    "ExtractedImage",
    "Entity",
    "Section",
    "ExtractionResult",
    "ProcessingConfig",
    "ClassificationResult",
    "ComparisonResult",
    # Main processor
    "DocumentProcessor",
    # Extractors
    "BaseExtractor",
    "TextExtractor",
    "HTMLExtractor",
    # Utilities
    "TableExtractor",
    "EntityExtractor",
    "DocumentChunker",
    "DocumentConverter",
]
