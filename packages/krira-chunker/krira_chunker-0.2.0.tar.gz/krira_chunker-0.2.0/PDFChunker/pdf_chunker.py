"""
PDF chunker for Krira_Chunker.
"""

import os
from typing import Generator, Dict, Any, Iterator

from ..config import ChunkConfig
from ..core import FastChunker, HybridBoundaryChunker, LOGGER, clean_text
from ..exceptions import (
    DependencyNotInstalledError,
    FileSizeLimitError,
    OCRRequiredError,
    ProcessingError,
)


class PDFChunker:
    """
    Class-based PDF chunker with lazy dependency loading.
    
    Example:
        >>> cfg = ChunkConfig(max_chars=2000)
        >>> chunker = PDFChunker(cfg)
        >>> for chunk in chunker.chunk_file("report.pdf"):
        ...     print(chunk["text"][:100])
    """
    
    def __init__(self, cfg: ChunkConfig = None):
        """
        Initialize PDF chunker with pdfplumber support.
        """
        self.cfg = cfg or ChunkConfig()
        self._parent_child_chunker = None
        self._hybrid_chunker = None

    @property
    def hybrid_chunker(self) -> HybridBoundaryChunker:
        """Lazy-load HybridBoundaryChunker."""
        if self._hybrid_chunker is None:
            self._hybrid_chunker = HybridBoundaryChunker(self.cfg)
        return self._hybrid_chunker

    def _get_pdfplumber(self):
        """Lazy import pdfplumber."""
        try:
            import pdfplumber
            return pdfplumber
        except ImportError:
            raise DependencyNotInstalledError("pdfplumber", "pdf", "Table-aware PDF processing")

    def _extract_page_content(self, page) -> str:
        """
        Extract content from a page, preserving table layout as Markdown.
        Strategy:
        1. Identify tables.
        2. "Crop" the page into vertical segments (Text -> Table -> Text).
        3. Extract text from text segments, extract markdown from table segments.
        """
        text_parts = []
        
        # 1. Find tables
        tables = page.find_tables()
        # Sort by top position just in case
        tables.sort(key=lambda t: t.bbox[1])
        
        current_y = 0
        page_height = page.height
        
        for table in tables:
            # table.bbox is (x0, top, x1, bottom)
            t_top, t_bottom = table.bbox[1], table.bbox[3]
            
            # --- Extract Text BEFORE Table ---
            if t_top > current_y:
                # Crop area above table
                # crop(x0, top, x1, bottom)
                # We want full width, from current_y to t_top
                try:
                    # page.crop argument is bounding box: (x0, top, x1, bottom)
                    # We use strict=False usually but pdfplumber crop expects exact bbox or similar
                    # Let's just use page.crop((0, current_y, page.width, t_top))
                    crop_area = page.crop((0, current_y, page.width, t_top))
                    
                    # Extract text naturally (layout=True keeps some structure)
                    text = crop_area.extract_text(layout=True) or ""
                    if text.strip():
                        text_parts.append(text)
                except Exception as e:
                    LOGGER.warning(f"Error cropping text pre-table: {e}")
            
            # --- Extract Table as Markdown ---
            try:
                # Extract clean table data
                # extract_table returns List[List[str]] or None
                table_data = table.extract()
                if table_data:
                     # Convert to Markdown
                     md_lines = []
                     # Header
                     if len(table_data) > 0:
                         headers = table_data[0]
                         # Clean None values
                         headers = [h if h else "" for h in headers]
                         md_lines.append("| " + " | ".join(headers) + " |")
                         md_lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
                         
                         # Body
                         for row in table_data[1:]:
                             row_clean = [c if c else "" for c in row]
                             md_lines.append("| " + " | ".join(row_clean) + " |")
                         
                         text_parts.append("\n" + "\n".join(md_lines) + "\n")
            except Exception as e:
                LOGGER.warning(f"Error extracting table markdown: {e}")
            
            current_y = t_bottom
            
        # --- Extract Remaining Text ---
        if current_y < page_height:
            try:
                crop_area = page.crop((0, current_y, page.width, page_height))
                text = crop_area.extract_text(layout=True) or ""
                if text.strip():
                    text_parts.append(text)
            except Exception as e:
                # If cropping fails (e.g. tiny slice), just ignore or log
                pass

        return "\n\n".join(text_parts)

    def chunk_file(
        self,
        file_path: str,
        raise_on_ocr_needed: bool = False,
    ) -> Iterator[Dict[str, Any]]:
        """Chunk a PDF file with table awareness."""
        pdfplumber = self._get_pdfplumber()
        cfg = self.cfg
        
        # Security check
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            if size > cfg.security_max_file_bytes:
                raise FileSizeLimitError(file_path, size, cfg.security_max_file_bytes)
        
        base_meta = {
            "source": os.path.basename(file_path),
            "source_path": os.path.abspath(file_path),
            "source_type": "pdf",
        }
        
        try:
            with pdfplumber.open(file_path) as pdf:
                total_pages = len(pdf.pages)
                chunk_index = 0
                
                # Check for Parent-Child strategy
                # If user wants parent-child, they might have setup a specific config or we wrapper it
                # But here we just use the text stream and feed it to the configured chunker strategy.
                # If cfg calls for "parent_child" we support it, but `cfg.chunk_strategy` is limited.
                # However, the USER asked us to "Implement Parent-Child Indexing" inside `core.py`.
                # And "Refactor PDFChunker...".
                # To actually USE Parent-Child, we likely need to detect it or use a specific class.
                # Since the instruction for core.py was "modify... (or create a new wrapper)", 
                # I'll default to standard hybrid chunking UNLESS we decide to expose ParentChild here.
                # Let's stick to standard behavior unless refactored deeper.
                # CHECK: User logic implies "Parent-Child" is the desirable retrieval logic.
                # I'll modify this to use ParentChildChunker if we can imply it, but `cfg` doesn't strictly have a flag.
                # I'll just use the standard `hybrid_chunker` for now as the prompt asked to *enable* the capability in core.py.
                # The PDFChunker's primary job is extracting *text with tables preserved*. 
                # Whether we chunk that text into parents/children is up to the *caller* or configuration of the chunker.
                
                # Wait, if I'm "Refactoring" to implement it, I should probably use it?
                # But the prompt split: 1. Modify core.py (Prep), 2. Refactor PDFChunker (Table Aware).
                # I will stick to extracting high quality text here.
                
                for i, page in enumerate(pdf.pages):
                    text = self._extract_page_content(page)
                    text = clean_text(text)
                    
                    if not text:
                        continue
                        
                    meta = dict(base_meta)
                    meta["page"] = i + 1
                    meta["total_pages"] = total_pages
                    
                    # Yield chunks using standard Hybrid to start, or we could add specific ParentChild call here
                    # For safety, I'll stick to configured strategy.
                    # The USER can now instantiate ParentChildChunker(cfg) manually and feed it text.
                    
                    for ch in self.hybrid_chunker.chunk_text(
                        text=text,
                        base_meta=meta,
                        locator=f"pdf|page={i+1}",
                        start_chunk_index=chunk_index,
                    ):
                        chunk_index = ch["metadata"]["chunk_index"] + 1
                        yield ch
                        
        except Exception as e:
            LOGGER.error("Error processing PDF %s: %s", file_path, e)
            raise ProcessingError(f"Failed to process PDF: {e}", {"path": file_path})


# Backward compatibility
def iter_chunks_from_pdf(
    file_path: str,
    cfg: ChunkConfig = None
) -> Generator[Dict[str, Any], None, None]:
    chunker = PDFChunker(cfg)
    yield from chunker.chunk_file(file_path)
