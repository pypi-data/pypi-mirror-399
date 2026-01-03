"""Document processing toolkit for AI applications."""

import hashlib
import mimetypes
import os
import re
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple, Union
from concurrent.futures import ThreadPoolExecutor, as_completed

from .types import (
    BoundingBox, ClassificationResult, ComparisonResult, DocumentElement,
    DocumentMetadata, DocumentType, ElementType, Entity, ExtractionMethod,
    ExtractionResult, ExtractedImage, LayoutType, PageInfo, ProcessingConfig,
    Section, Table, TableCell, TableFormat
)


class BaseExtractor(ABC):
    """Base class for document extractors."""
    
    @abstractmethod
    def extract(self, source: Union[str, bytes, Path],
                config: ProcessingConfig) -> ExtractionResult:
        """Extract content from document."""
        pass
    
    @abstractmethod
    def supports(self, doc_type: DocumentType) -> bool:
        """Check if extractor supports document type."""
        pass


class TextExtractor(BaseExtractor):
    """Plain text file extractor."""
    
    def extract(self, source: Union[str, bytes, Path],
                config: ProcessingConfig) -> ExtractionResult:
        start_time = time.time()
        
        if isinstance(source, bytes):
            text = source.decode("utf-8", errors="replace")
            filename = "document.txt"
            file_size = len(source)
        else:
            path = Path(source)
            text = path.read_text(encoding="utf-8", errors="replace")
            filename = path.name
            file_size = path.stat().st_size
        
        elements = self._parse_elements(text)
        
        metadata = DocumentMetadata(
            filename=filename,
            file_size=file_size,
            page_count=1,
            doc_type=DocumentType.TXT
        )
        
        pages = [PageInfo(number=1, width=0, height=0)]
        
        return ExtractionResult(
            text=text,
            elements=elements,
            tables=[],
            images=[],
            metadata=metadata,
            pages=pages,
            extraction_method=ExtractionMethod.NATIVE,
            processing_time=time.time() - start_time
        )
    
    def _parse_elements(self, text: str) -> List[DocumentElement]:
        """Parse text into elements."""
        elements = []
        paragraphs = text.split("\n\n")
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            if para.startswith("#"):
                elem_type = ElementType.HEADING
            elif para.startswith("-") or para.startswith("*"):
                elem_type = ElementType.LIST
            elif para.startswith(">"):
                elem_type = ElementType.QUOTE
            elif para.startswith("```") or para.startswith("    "):
                elem_type = ElementType.CODE
            else:
                elem_type = ElementType.PARAGRAPH
            
            elements.append(DocumentElement(
                type=elem_type,
                content=para,
                page=1
            ))
        
        return elements
    
    def supports(self, doc_type: DocumentType) -> bool:
        return doc_type in (DocumentType.TXT, DocumentType.MARKDOWN)


class HTMLExtractor(BaseExtractor):
    """HTML document extractor."""
    
    def extract(self, source: Union[str, bytes, Path],
                config: ProcessingConfig) -> ExtractionResult:
        start_time = time.time()
        
        if isinstance(source, bytes):
            html = source.decode("utf-8", errors="replace")
            filename = "document.html"
            file_size = len(source)
        elif isinstance(source, Path) or (isinstance(source, str) and os.path.exists(source)):
            path = Path(source)
            html = path.read_text(encoding="utf-8", errors="replace")
            filename = path.name
            file_size = path.stat().st_size
        else:
            html = source
            filename = "document.html"
            file_size = len(source.encode())
        
        text = self._strip_html(html)
        elements = self._parse_html_elements(html)
        tables = self._extract_tables(html) if config.extract_tables else []
        metadata = self._extract_metadata(html, filename, file_size)
        
        return ExtractionResult(
            text=text,
            elements=elements,
            tables=tables,
            images=[],
            metadata=metadata,
            pages=[PageInfo(number=1, width=0, height=0)],
            extraction_method=ExtractionMethod.NATIVE,
            processing_time=time.time() - start_time
        )
    
    def _strip_html(self, html: str) -> str:
        """Remove HTML tags and get plain text."""
        html = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r"<[^>]+>", " ", html)
        html = re.sub(r"\s+", " ", html)
        return html.strip()
    
    def _parse_html_elements(self, html: str) -> List[DocumentElement]:
        """Parse HTML into elements."""
        elements = []
        
        tag_patterns = [
            (r"<h[1-6][^>]*>(.*?)</h[1-6]>", ElementType.HEADING),
            (r"<p[^>]*>(.*?)</p>", ElementType.PARAGRAPH),
            (r"<li[^>]*>(.*?)</li>", ElementType.LIST_ITEM),
            (r"<blockquote[^>]*>(.*?)</blockquote>", ElementType.QUOTE),
            (r"<code[^>]*>(.*?)</code>", ElementType.CODE),
            (r"<pre[^>]*>(.*?)</pre>", ElementType.CODE),
        ]
        
        for pattern, elem_type in tag_patterns:
            for match in re.finditer(pattern, html, re.DOTALL | re.IGNORECASE):
                content = self._strip_html(match.group(1))
                if content:
                    elements.append(DocumentElement(
                        type=elem_type,
                        content=content,
                        page=1
                    ))
        
        return elements
    
    def _extract_tables(self, html: str) -> List[Table]:
        """Extract tables from HTML."""
        tables = []
        table_pattern = r"<table[^>]*>(.*?)</table>"
        
        for match in re.finditer(table_pattern, html, re.DOTALL | re.IGNORECASE):
            table_html = match.group(1)
            cells = []
            rows = 0
            max_cols = 0
            
            row_pattern = r"<tr[^>]*>(.*?)</tr>"
            for row_match in re.finditer(row_pattern, table_html, re.DOTALL | re.IGNORECASE):
                row_html = row_match.group(1)
                col = 0
                
                cell_pattern = r"<(th|td)[^>]*>(.*?)</(?:th|td)>"
                for cell_match in re.finditer(cell_pattern, row_html, re.DOTALL | re.IGNORECASE):
                    is_header = cell_match.group(1).lower() == "th"
                    content = self._strip_html(cell_match.group(2))
                    
                    cells.append(TableCell(
                        content=content,
                        row=rows,
                        col=col,
                        is_header=is_header
                    ))
                    col += 1
                
                max_cols = max(max_cols, col)
                rows += 1
            
            if cells:
                tables.append(Table(
                    cells=cells,
                    rows=rows,
                    cols=max_cols,
                    page=1
                ))
        
        return tables
    
    def _extract_metadata(self, html: str, filename: str, file_size: int) -> DocumentMetadata:
        """Extract metadata from HTML."""
        title = None
        title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
        if title_match:
            title = self._strip_html(title_match.group(1))
        
        author = None
        author_match = re.search(r'<meta[^>]+name=["\']author["\'][^>]+content=["\']([^"\']+)["\']', html, re.IGNORECASE)
        if author_match:
            author = author_match.group(1)
        
        return DocumentMetadata(
            filename=filename,
            file_size=file_size,
            page_count=1,
            doc_type=DocumentType.HTML,
            title=title,
            author=author
        )
    
    def supports(self, doc_type: DocumentType) -> bool:
        return doc_type == DocumentType.HTML


class DocumentProcessor:
    """Main document processor with multiple extractors."""
    
    def __init__(self, config: Optional[ProcessingConfig] = None):
        """Initialize processor.
        
        Args:
            config: Default processing configuration
        """
        self.config = config or ProcessingConfig()
        self.extractors: List[BaseExtractor] = [
            TextExtractor(),
            HTMLExtractor(),
        ]
        self._custom_extractors: Dict[DocumentType, BaseExtractor] = {}
        self._entity_extractors: List[Callable[[str], List[Entity]]] = []
        self._classifiers: Dict[str, Callable[[ExtractionResult], ClassificationResult]] = {}
    
    def register_extractor(self, doc_type: DocumentType, extractor: BaseExtractor) -> None:
        """Register custom extractor for document type."""
        self._custom_extractors[doc_type] = extractor
    
    def register_entity_extractor(self, extractor: Callable[[str], List[Entity]]) -> None:
        """Register entity extractor."""
        self._entity_extractors.append(extractor)
    
    def register_classifier(self, name: str, 
                           classifier: Callable[[ExtractionResult], ClassificationResult]) -> None:
        """Register document classifier."""
        self._classifiers[name] = classifier
    
    def detect_type(self, source: Union[str, bytes, Path]) -> DocumentType:
        """Detect document type from source."""
        if isinstance(source, bytes):
            if source.startswith(b"%PDF"):
                return DocumentType.PDF
            elif source.startswith(b"PK"):
                return DocumentType.DOCX
            elif b"<html" in source.lower()[:1000]:
                return DocumentType.HTML
            return DocumentType.TXT
        
        path = Path(source)
        ext = path.suffix.lower()
        
        type_map = {
            ".pdf": DocumentType.PDF,
            ".docx": DocumentType.DOCX,
            ".doc": DocumentType.DOC,
            ".txt": DocumentType.TXT,
            ".html": DocumentType.HTML,
            ".htm": DocumentType.HTML,
            ".md": DocumentType.MARKDOWN,
            ".xlsx": DocumentType.SPREADSHEET,
            ".xls": DocumentType.SPREADSHEET,
            ".csv": DocumentType.SPREADSHEET,
            ".pptx": DocumentType.PRESENTATION,
            ".ppt": DocumentType.PRESENTATION,
            ".eml": DocumentType.EMAIL,
            ".png": DocumentType.IMAGE,
            ".jpg": DocumentType.IMAGE,
            ".jpeg": DocumentType.IMAGE,
            ".gif": DocumentType.IMAGE,
            ".tiff": DocumentType.IMAGE,
            ".bmp": DocumentType.IMAGE,
        }
        
        return type_map.get(ext, DocumentType.UNKNOWN)
    
    def process(self, source: Union[str, bytes, Path],
                config: Optional[ProcessingConfig] = None) -> ExtractionResult:
        """Process a document and extract content.
        
        Args:
            source: File path, bytes, or string content
            config: Processing configuration (uses default if not provided)
            
        Returns:
            ExtractionResult with extracted content
        """
        config = config or self.config
        doc_type = self.detect_type(source)
        
        if doc_type in self._custom_extractors:
            result = self._custom_extractors[doc_type].extract(source, config)
        else:
            extractor = self._find_extractor(doc_type)
            if extractor:
                result = extractor.extract(source, config)
            else:
                if isinstance(source, bytes):
                    text = source.decode("utf-8", errors="replace")
                    filename = "document"
                else:
                    path = Path(source)
                    text = path.read_text(errors="replace") if path.exists() else str(source)
                    filename = path.name if path.exists() else "document"
                
                result = ExtractionResult(
                    text=text,
                    elements=[DocumentElement(type=ElementType.PARAGRAPH, content=text)],
                    tables=[],
                    images=[],
                    metadata=DocumentMetadata(filename=filename, doc_type=doc_type),
                    pages=[PageInfo(number=1, width=0, height=0)],
                    warnings=[f"No specialized extractor for {doc_type.value}"]
                )
        
        if config.detect_entities and self._entity_extractors:
            for extractor in self._entity_extractors:
                result.entities.extend(extractor(result.text))
        
        if config.detect_layout:
            result.sections = self._detect_sections(result.elements)
        
        return result
    
    def _find_extractor(self, doc_type: DocumentType) -> Optional[BaseExtractor]:
        """Find suitable extractor for document type."""
        for extractor in self.extractors:
            if extractor.supports(doc_type):
                return extractor
        return None
    
    def _detect_sections(self, elements: List[DocumentElement]) -> List[Section]:
        """Detect document sections from elements."""
        sections = []
        current_section = None
        
        for element in elements:
            if element.type in (ElementType.TITLE, ElementType.HEADING):
                if current_section:
                    sections.append(current_section)
                
                level = 1
                if element.content.startswith("##"):
                    level = element.content.count("#", 0, 6)
                
                current_section = Section(
                    title=element.content.lstrip("#").strip(),
                    content="",
                    level=level,
                    page_start=element.page,
                    page_end=element.page,
                    elements=[element]
                )
            elif current_section:
                current_section.elements.append(element)
                current_section.content += element.content + "\n"
                current_section.page_end = element.page
        
        if current_section:
            sections.append(current_section)
        
        return sections
    
    def process_batch(self, sources: List[Union[str, bytes, Path]],
                      config: Optional[ProcessingConfig] = None,
                      max_workers: int = 4) -> List[ExtractionResult]:
        """Process multiple documents in parallel.
        
        Args:
            sources: List of document sources
            config: Processing configuration
            max_workers: Maximum parallel workers
            
        Returns:
            List of extraction results
        """
        config = config or self.config
        results = [None] * len(sources)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self.process, source, config): i
                for i, source in enumerate(sources)
            }
            
            for future in as_completed(futures):
                idx = futures[future]
                try:
                    results[idx] = future.result()
                except Exception as e:
                    results[idx] = ExtractionResult(
                        text="",
                        elements=[],
                        tables=[],
                        images=[],
                        metadata=DocumentMetadata(filename=str(sources[idx])),
                        pages=[],
                        warnings=[f"Processing failed: {str(e)}"]
                    )
        
        return results
    
    def classify(self, result: ExtractionResult, 
                classifier_name: Optional[str] = None) -> ClassificationResult:
        """Classify a document.
        
        Args:
            result: Extraction result to classify
            classifier_name: Specific classifier to use
            
        Returns:
            Classification result
        """
        if classifier_name and classifier_name in self._classifiers:
            return self._classifiers[classifier_name](result)
        
        if self._classifiers:
            name, classifier = next(iter(self._classifiers.items()))
            return classifier(result)
        
        return self._default_classify(result)
    
    def _default_classify(self, result: ExtractionResult) -> ClassificationResult:
        """Default rule-based classification."""
        text_lower = result.text.lower()
        
        categories = {
            "invoice": ["invoice", "bill to", "amount due", "payment"],
            "contract": ["agreement", "hereby", "parties", "whereas", "terms"],
            "report": ["summary", "findings", "analysis", "conclusion"],
            "resume": ["experience", "education", "skills", "references"],
            "letter": ["dear", "sincerely", "regards", "yours"],
            "form": ["please fill", "required field", "signature", "date:"],
            "technical": ["api", "implementation", "function", "class", "method"],
        }
        
        scores = {}
        for category, keywords in categories.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            scores[category] = score / len(keywords)
        
        if scores:
            best_category = max(scores, key=scores.get)
            confidence = scores[best_category]
        else:
            best_category = "unknown"
            confidence = 0.0
        
        return ClassificationResult(
            label=best_category,
            confidence=confidence,
            all_scores=scores,
            features={
                "word_count": len(result.text.split()),
                "table_count": len(result.tables),
                "page_count": len(result.pages)
            }
        )
    
    def compare(self, result1: ExtractionResult, 
               result2: ExtractionResult) -> ComparisonResult:
        """Compare two documents.
        
        Args:
            result1: First document
            result2: Second document
            
        Returns:
            Comparison result
        """
        lines1 = set(result1.text.split("\n"))
        lines2 = set(result2.text.split("\n"))
        
        added = list(lines2 - lines1)
        removed = list(lines1 - lines2)
        
        words1 = set(result1.text.lower().split())
        words2 = set(result2.text.lower().split())
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        similarity = intersection / union if union > 0 else 0.0
        
        metadata_diff = {}
        if result1.metadata.title != result2.metadata.title:
            metadata_diff["title"] = (result1.metadata.title, result2.metadata.title)
        if result1.metadata.author != result2.metadata.author:
            metadata_diff["author"] = (result1.metadata.author, result2.metadata.author)
        
        return ComparisonResult(
            similarity=similarity,
            added=added[:100],
            removed=removed[:100],
            modified=[],
            metadata_diff=metadata_diff
        )


class TableExtractor:
    """Specialized table extraction utilities."""
    
    @staticmethod
    def from_text(text: str, delimiter: str = "|") -> Optional[Table]:
        """Extract table from delimiter-separated text."""
        lines = [l.strip() for l in text.strip().split("\n") if l.strip()]
        if len(lines) < 2:
            return None
        
        cells = []
        rows = 0
        max_cols = 0
        
        for line in lines:
            if set(line.replace(delimiter, "").strip()) <= {"-", ":", " "}:
                continue
            
            cols = [c.strip() for c in line.split(delimiter) if c.strip()]
            for col_idx, content in enumerate(cols):
                cells.append(TableCell(
                    content=content,
                    row=rows,
                    col=col_idx,
                    is_header=(rows == 0)
                ))
            max_cols = max(max_cols, len(cols))
            rows += 1
        
        return Table(cells=cells, rows=rows, cols=max_cols) if cells else None
    
    @staticmethod
    def from_csv(csv_text: str) -> Optional[Table]:
        """Extract table from CSV text."""
        lines = csv_text.strip().split("\n")
        if not lines:
            return None
        
        cells = []
        rows = 0
        max_cols = 0
        
        for line in lines:
            cols = []
            current = ""
            in_quotes = False
            
            for char in line:
                if char == '"':
                    in_quotes = not in_quotes
                elif char == "," and not in_quotes:
                    cols.append(current.strip().strip('"'))
                    current = ""
                else:
                    current += char
            cols.append(current.strip().strip('"'))
            
            for col_idx, content in enumerate(cols):
                cells.append(TableCell(
                    content=content,
                    row=rows,
                    col=col_idx,
                    is_header=(rows == 0)
                ))
            max_cols = max(max_cols, len(cols))
            rows += 1
        
        return Table(cells=cells, rows=rows, cols=max_cols) if cells else None
    
    @staticmethod
    def merge_tables(tables: List[Table], axis: int = 0) -> Table:
        """Merge multiple tables.
        
        Args:
            tables: Tables to merge
            axis: 0 for vertical (append rows), 1 for horizontal (append columns)
        """
        if not tables:
            return Table(cells=[], rows=0, cols=0)
        
        if len(tables) == 1:
            return tables[0]
        
        all_cells = []
        
        if axis == 0:
            total_rows = 0
            max_cols = max(t.cols for t in tables)
            
            for table in tables:
                for cell in table.cells:
                    all_cells.append(TableCell(
                        content=cell.content,
                        row=cell.row + total_rows,
                        col=cell.col,
                        rowspan=cell.rowspan,
                        colspan=cell.colspan,
                        is_header=cell.is_header and total_rows == 0
                    ))
                total_rows += table.rows
            
            return Table(cells=all_cells, rows=total_rows, cols=max_cols)
        else:
            max_rows = max(t.rows for t in tables)
            total_cols = 0
            
            for table in tables:
                for cell in table.cells:
                    all_cells.append(TableCell(
                        content=cell.content,
                        row=cell.row,
                        col=cell.col + total_cols,
                        rowspan=cell.rowspan,
                        colspan=cell.colspan,
                        is_header=cell.is_header
                    ))
                total_cols += table.cols
            
            return Table(cells=all_cells, rows=max_rows, cols=total_cols)


class EntityExtractor:
    """Built-in entity extraction patterns."""
    
    PATTERNS = {
        "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "PHONE": r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
        "URL": r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[/\w\-._~:/?#\[\]@!$&'()*+,;=]*",
        "DATE": r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b",
        "MONEY": r"\$\s?\d+(?:,\d{3})*(?:\.\d{2})?|\d+(?:,\d{3})*(?:\.\d{2})?\s?(?:USD|EUR|GBP)",
        "PERCENTAGE": r"\b\d+(?:\.\d+)?%\b",
        "SSN": r"\b\d{3}-\d{2}-\d{4}\b",
        "CREDIT_CARD": r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
        "IP_ADDRESS": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
    }
    
    def __init__(self, patterns: Optional[Dict[str, str]] = None):
        """Initialize with patterns.
        
        Args:
            patterns: Custom regex patterns {label: pattern}
        """
        self.patterns = {**self.PATTERNS}
        if patterns:
            self.patterns.update(patterns)
    
    def extract(self, text: str) -> List[Entity]:
        """Extract entities from text."""
        entities = []
        
        for label, pattern in self.patterns.items():
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(Entity(
                    text=match.group(),
                    label=label,
                    start=match.start(),
                    end=match.end(),
                    confidence=1.0
                ))
        
        entities.sort(key=lambda e: e.start)
        return entities


class DocumentChunker:
    """Split documents into chunks for processing."""
    
    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        """Initialize chunker.
        
        Args:
            chunk_size: Target chunk size in characters
            overlap: Overlap between chunks
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks."""
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            if end < len(text):
                break_point = text.rfind(". ", start, end)
                if break_point == -1 or break_point <= start:
                    break_point = text.rfind(" ", start, end)
                if break_point > start:
                    end = break_point + 1
            
            chunks.append(text[start:end].strip())
            start = end - self.overlap
        
        return chunks
    
    def chunk_by_sections(self, result: ExtractionResult) -> List[str]:
        """Chunk document by sections."""
        if not result.sections:
            return self.chunk_text(result.text)
        
        chunks = []
        for section in result.sections:
            section_text = f"{section.title}\n\n{section.content}"
            if len(section_text) <= self.chunk_size:
                chunks.append(section_text)
            else:
                chunks.extend(self.chunk_text(section_text))
        
        return chunks
    
    def chunk_by_elements(self, result: ExtractionResult) -> List[str]:
        """Chunk document by elements."""
        chunks = []
        current_chunk = ""
        
        for element in result.elements:
            element_text = element.content
            
            if len(current_chunk) + len(element_text) > self.chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                if len(element_text) > self.chunk_size:
                    chunks.extend(self.chunk_text(element_text))
                    current_chunk = ""
                else:
                    current_chunk = element_text
            else:
                current_chunk += "\n\n" + element_text if current_chunk else element_text
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks


class DocumentConverter:
    """Convert between document formats."""
    
    @staticmethod
    def to_markdown(result: ExtractionResult) -> str:
        """Convert extraction result to markdown."""
        lines = []
        
        if result.metadata.title:
            lines.append(f"# {result.metadata.title}\n")
        
        for element in result.elements:
            if element.type == ElementType.TITLE:
                lines.append(f"# {element.content}\n")
            elif element.type == ElementType.HEADING:
                level = element.metadata.get("level", 2)
                lines.append(f"{'#' * level} {element.content}\n")
            elif element.type == ElementType.PARAGRAPH:
                lines.append(f"{element.content}\n")
            elif element.type == ElementType.LIST_ITEM:
                lines.append(f"- {element.content}")
            elif element.type == ElementType.CODE:
                lines.append(f"```\n{element.content}\n```\n")
            elif element.type == ElementType.QUOTE:
                lines.append(f"> {element.content}\n")
        
        for table in result.tables:
            lines.append("\n" + table.to_markdown() + "\n")
        
        return "\n".join(lines)
    
    @staticmethod
    def to_html(result: ExtractionResult) -> str:
        """Convert extraction result to HTML."""
        parts = ["<!DOCTYPE html><html><head>"]
        
        if result.metadata.title:
            parts.append(f"<title>{result.metadata.title}</title>")
        
        parts.append("</head><body>")
        
        for element in result.elements:
            content = element.content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            
            if element.type == ElementType.TITLE:
                parts.append(f"<h1>{content}</h1>")
            elif element.type == ElementType.HEADING:
                level = min(element.metadata.get("level", 2), 6)
                parts.append(f"<h{level}>{content}</h{level}>")
            elif element.type == ElementType.PARAGRAPH:
                parts.append(f"<p>{content}</p>")
            elif element.type == ElementType.LIST_ITEM:
                parts.append(f"<li>{content}</li>")
            elif element.type == ElementType.CODE:
                parts.append(f"<pre><code>{content}</code></pre>")
            elif element.type == ElementType.QUOTE:
                parts.append(f"<blockquote>{content}</blockquote>")
        
        for table in result.tables:
            parts.append("<table border='1'>")
            grid = table.to_list()
            for i, row in enumerate(grid):
                parts.append("<tr>")
                tag = "th" if i == 0 else "td"
                for cell in row:
                    parts.append(f"<{tag}>{cell}</{tag}>")
                parts.append("</tr>")
            parts.append("</table>")
        
        parts.append("</body></html>")
        return "\n".join(parts)
    
    @staticmethod
    def to_json(result: ExtractionResult) -> str:
        """Convert extraction result to JSON."""
        import json
        return json.dumps(result.to_dict(), indent=2, default=str)
