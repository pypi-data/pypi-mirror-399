"""Type definitions for document-ai-toolkit."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime


class DocumentType(Enum):
    """Supported document types."""
    PDF = "pdf"
    DOCX = "docx"
    DOC = "doc"
    TXT = "txt"
    HTML = "html"
    MARKDOWN = "markdown"
    IMAGE = "image"
    SPREADSHEET = "spreadsheet"
    PRESENTATION = "presentation"
    EMAIL = "email"
    UNKNOWN = "unknown"


class ElementType(Enum):
    """Document element types."""
    TITLE = "title"
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    LIST = "list"
    LIST_ITEM = "list_item"
    TABLE = "table"
    IMAGE = "image"
    FIGURE = "figure"
    CAPTION = "caption"
    HEADER = "header"
    FOOTER = "footer"
    FOOTNOTE = "footnote"
    CODE = "code"
    QUOTE = "quote"
    LINK = "link"
    FORMULA = "formula"
    PAGE_BREAK = "page_break"
    UNKNOWN = "unknown"


class ExtractionMethod(Enum):
    """Text extraction methods."""
    NATIVE = "native"
    OCR = "ocr"
    HYBRID = "hybrid"
    ML_BASED = "ml_based"


class TableFormat(Enum):
    """Table output formats."""
    DICT = "dict"
    LIST = "list"
    MARKDOWN = "markdown"
    HTML = "html"
    CSV = "csv"
    DATAFRAME = "dataframe"


class LayoutType(Enum):
    """Document layout types."""
    SINGLE_COLUMN = "single_column"
    MULTI_COLUMN = "multi_column"
    MIXED = "mixed"
    FORM = "form"
    TABULAR = "tabular"


@dataclass
class BoundingBox:
    """Bounding box coordinates."""
    x1: float
    y1: float
    x2: float
    y2: float
    page: int = 1
    
    @property
    def width(self) -> float:
        return self.x2 - self.x1
    
    @property
    def height(self) -> float:
        return self.y2 - self.y1
    
    @property
    def area(self) -> float:
        return self.width * self.height
    
    @property
    def center(self) -> Tuple[float, float]:
        return ((self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2)
    
    def contains(self, other: "BoundingBox") -> bool:
        """Check if this box contains another."""
        return (self.x1 <= other.x1 and self.y1 <= other.y1 and
                self.x2 >= other.x2 and self.y2 >= other.y2)
    
    def overlaps(self, other: "BoundingBox") -> bool:
        """Check if boxes overlap."""
        return not (self.x2 < other.x1 or self.x1 > other.x2 or
                    self.y2 < other.y1 or self.y1 > other.y2)
    
    def iou(self, other: "BoundingBox") -> float:
        """Calculate intersection over union."""
        x1 = max(self.x1, other.x1)
        y1 = max(self.y1, other.y1)
        x2 = min(self.x2, other.x2)
        y2 = min(self.y2, other.y2)
        
        if x2 < x1 or y2 < y1:
            return 0.0
        
        intersection = (x2 - x1) * (y2 - y1)
        union = self.area + other.area - intersection
        return intersection / union if union > 0 else 0.0


@dataclass
class DocumentElement:
    """A single document element."""
    type: ElementType
    content: str
    bbox: Optional[BoundingBox] = None
    page: int = 1
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    children: List["DocumentElement"] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "content": self.content,
            "bbox": {
                "x1": self.bbox.x1, "y1": self.bbox.y1,
                "x2": self.bbox.x2, "y2": self.bbox.y2
            } if self.bbox else None,
            "page": self.page,
            "confidence": self.confidence,
            "metadata": self.metadata,
            "children": [c.to_dict() for c in self.children]
        }


@dataclass
class TableCell:
    """A table cell."""
    content: str
    row: int
    col: int
    rowspan: int = 1
    colspan: int = 1
    is_header: bool = False
    bbox: Optional[BoundingBox] = None
    confidence: float = 1.0


@dataclass
class Table:
    """An extracted table."""
    cells: List[TableCell]
    rows: int
    cols: int
    page: int = 1
    bbox: Optional[BoundingBox] = None
    caption: Optional[str] = None
    confidence: float = 1.0
    
    def to_list(self) -> List[List[str]]:
        """Convert to 2D list."""
        grid = [["" for _ in range(self.cols)] for _ in range(self.rows)]
        for cell in self.cells:
            for r in range(cell.row, cell.row + cell.rowspan):
                for c in range(cell.col, cell.col + cell.colspan):
                    if r < self.rows and c < self.cols:
                        grid[r][c] = cell.content
        return grid
    
    def to_dict(self) -> Dict[str, List[Any]]:
        """Convert to dict with headers as keys."""
        grid = self.to_list()
        if not grid:
            return {}
        headers = grid[0]
        return {
            h: [row[i] if i < len(row) else "" for row in grid[1:]]
            for i, h in enumerate(headers)
        }
    
    def to_markdown(self) -> str:
        """Convert to markdown table."""
        grid = self.to_list()
        if not grid:
            return ""
        lines = []
        lines.append("| " + " | ".join(grid[0]) + " |")
        lines.append("| " + " | ".join(["---"] * len(grid[0])) + " |")
        for row in grid[1:]:
            lines.append("| " + " | ".join(row) + " |")
        return "\n".join(lines)
    
    def to_csv(self) -> str:
        """Convert to CSV string."""
        grid = self.to_list()
        lines = []
        for row in grid:
            escaped = [f'"{c.replace(chr(34), chr(34)+chr(34))}"' if "," in c or '"' in c else c for c in row]
            lines.append(",".join(escaped))
        return "\n".join(lines)


@dataclass
class PageInfo:
    """Page information."""
    number: int
    width: float
    height: float
    rotation: int = 0
    dpi: int = 72
    has_text: bool = True
    has_images: bool = False
    layout: LayoutType = LayoutType.SINGLE_COLUMN


@dataclass
class DocumentMetadata:
    """Document metadata."""
    filename: str
    file_size: int = 0
    page_count: int = 0
    doc_type: DocumentType = DocumentType.UNKNOWN
    title: Optional[str] = None
    author: Optional[str] = None
    subject: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    created: Optional[datetime] = None
    modified: Optional[datetime] = None
    language: Optional[str] = None
    producer: Optional[str] = None
    encrypted: bool = False
    custom: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExtractedImage:
    """An extracted image."""
    data: bytes
    format: str
    width: int
    height: int
    page: int
    bbox: Optional[BoundingBox] = None
    caption: Optional[str] = None
    alt_text: Optional[str] = None


@dataclass
class Entity:
    """An extracted entity."""
    text: str
    label: str
    start: int
    end: int
    confidence: float = 1.0
    page: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Section:
    """A document section."""
    title: str
    content: str
    level: int
    page_start: int
    page_end: int
    elements: List[DocumentElement] = field(default_factory=list)
    subsections: List["Section"] = field(default_factory=list)


@dataclass
class ExtractionResult:
    """Result of document extraction."""
    text: str
    elements: List[DocumentElement]
    tables: List[Table]
    images: List[ExtractedImage]
    metadata: DocumentMetadata
    pages: List[PageInfo]
    sections: List[Section] = field(default_factory=list)
    entities: List[Entity] = field(default_factory=list)
    extraction_method: ExtractionMethod = ExtractionMethod.NATIVE
    processing_time: float = 0.0
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "elements": [e.to_dict() for e in self.elements],
            "tables": [t.to_dict() for t in self.tables],
            "image_count": len(self.images),
            "metadata": {
                "filename": self.metadata.filename,
                "page_count": self.metadata.page_count,
                "doc_type": self.metadata.doc_type.value,
                "title": self.metadata.title,
                "author": self.metadata.author
            },
            "page_count": len(self.pages),
            "section_count": len(self.sections),
            "entity_count": len(self.entities),
            "extraction_method": self.extraction_method.value,
            "processing_time": self.processing_time,
            "warnings": self.warnings
        }


@dataclass
class ProcessingConfig:
    """Configuration for document processing."""
    extract_text: bool = True
    extract_tables: bool = True
    extract_images: bool = False
    extract_metadata: bool = True
    detect_layout: bool = True
    detect_entities: bool = False
    ocr_enabled: bool = False
    ocr_language: str = "eng"
    table_format: TableFormat = TableFormat.DICT
    max_pages: Optional[int] = None
    page_range: Optional[Tuple[int, int]] = None
    dpi: int = 300
    preserve_whitespace: bool = False
    merge_lines: bool = True
    detect_headers_footers: bool = True
    custom_entity_types: List[str] = field(default_factory=list)


@dataclass
class ClassificationResult:
    """Document classification result."""
    label: str
    confidence: float
    all_scores: Dict[str, float] = field(default_factory=dict)
    features: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ComparisonResult:
    """Document comparison result."""
    similarity: float
    added: List[str]
    removed: List[str]
    modified: List[Tuple[str, str]]
    metadata_diff: Dict[str, Tuple[Any, Any]] = field(default_factory=dict)
