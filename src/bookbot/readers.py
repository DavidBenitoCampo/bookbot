"""
BookBot File Readers - Multi-format file reading support.

Provides unified interface for reading text from various file formats:
- Plain text (.txt, .md, .text)
- PDF documents (.pdf)
- EPUB ebooks (.epub)
"""

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Dict, Type
import re

logger = logging.getLogger(__name__)

# Try importing optional dependencies
try:
    # Try pypdf first (modern version)
    import pypdf
    HAS_PYPDF = True
    PyPDF2 = None  # Mark as not using legacy
except ImportError:
    try:
        # Fall back to PyPDF2 (deprecated but still works)
        import PyPDF2
        HAS_PYPDF = True
    except ImportError:
        HAS_PYPDF = False
        PyPDF2 = None
        logger.debug("pypdf/PyPDF2 not installed. PDF support disabled.")


try:
    import ebooklib
    from ebooklib import epub
    HAS_EBOOKLIB = True
except ImportError:
    HAS_EBOOKLIB = False
    logger.debug("ebooklib not installed. EPUB support disabled.")

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False
    logger.debug("BeautifulSoup not installed. EPUB content parsing may be limited.")


class FileReaderError(Exception):
    """Base exception for file reader errors."""
    pass


class UnsupportedFormatError(FileReaderError):
    """Raised when file format is not supported."""
    pass


class FileReadError(FileReaderError):
    """Raised when file cannot be read."""
    pass


class BaseReader(ABC):
    """Abstract base class for file readers."""
    
    supported_extensions: list = []
    
    @abstractmethod
    def read(self, file_path: Path) -> str:
        """
        Read text content from a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Extracted text content
        """
        pass
    
    @classmethod
    def can_read(cls, file_path: Path) -> bool:
        """Check if this reader can handle the given file."""
        return file_path.suffix.lower() in cls.supported_extensions


class TextReader(BaseReader):
    """Reader for plain text files."""
    
    supported_extensions = ['.txt', '.text', '.md', '.markdown', '.rst']
    
    def __init__(self, encoding: Optional[str] = None):
        self.encoding = encoding
    
    def _detect_encoding(self, file_path: Path) -> str:
        """Detect file encoding by trying common encodings."""
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for enc in encodings:
            try:
                with open(file_path, 'r', encoding=enc) as f:
                    f.read(1024)
                return enc
            except (UnicodeDecodeError, UnicodeError):
                continue
        
        return 'utf-8'  # Default fallback
    
    def read(self, file_path: Path) -> str:
        """Read text from a plain text file."""
        if not file_path.exists():
            raise FileReadError(f"File not found: {file_path}")
        
        encoding = self.encoding or self._detect_encoding(file_path)
        
        try:
            return file_path.read_text(encoding=encoding)
        except Exception as e:
            raise FileReadError(f"Error reading {file_path}: {e}")


class PDFReader(BaseReader):
    """Reader for PDF documents."""
    
    supported_extensions = ['.pdf']
    
    def read(self, file_path: Path) -> str:
        """Extract text from a PDF file."""
        if not HAS_PYPDF:
            raise UnsupportedFormatError(
                "PDF support requires pypdf. Install with: pip install pypdf"
            )
        
        if not file_path.exists():
            raise FileReadError(f"File not found: {file_path}")
        
        try:
            text_parts = []
            
            with open(file_path, 'rb') as f:
                # Use pypdf or PyPDF2 based on what's available
                if PyPDF2 is None:
                    reader = pypdf.PdfReader(f)
                else:
                    reader = PyPDF2.PdfReader(f)
                
                logger.info(f"Reading PDF with {len(reader.pages)} pages")
                
                for i, page in enumerate(reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text_parts.append(page_text)
                    except Exception as e:
                        logger.warning(f"Error extracting page {i + 1}: {e}")
                        continue
            
            text = '\n\n'.join(text_parts)
            
            # Clean up common PDF artifacts
            text = self._clean_pdf_text(text)
            
            if not text.strip():
                raise FileReadError(
                    f"No text could be extracted from PDF: {file_path}. "
                    "This might be a scanned/image-based PDF."
                )
            
            return text
            
        except Exception as e:
            # Handle PyPDF2/pypdf errors
            if 'PdfReadError' in str(type(e).__name__):
                raise FileReadError(f"Invalid PDF file {file_path}: {e}")
            if isinstance(e, FileReadError):
                raise
            raise FileReadError(f"Error reading PDF {file_path}: {e}")

    
    def _clean_pdf_text(self, text: str) -> str:
        """Clean up common PDF extraction artifacts."""
        # Fix hyphenation at line breaks
        text = re.sub(r'-\n(\w)', r'\1', text)
        
        # Normalize whitespace
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Fix multiple newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()


class EPUBReader(BaseReader):
    """Reader for EPUB ebooks."""
    
    supported_extensions = ['.epub']
    
    def read(self, file_path: Path) -> str:
        """Extract text from an EPUB file."""
        if not HAS_EBOOKLIB:
            raise UnsupportedFormatError(
                "EPUB support requires ebooklib. Install with: pip install ebooklib"
            )
        
        if not file_path.exists():
            raise FileReadError(f"File not found: {file_path}")
        
        try:
            book = epub.read_epub(str(file_path))
            text_parts = []
            
            # Get all document items (chapters)
            for item in book.get_items():
                if item.get_type() == ebooklib.ITEM_DOCUMENT:
                    content = item.get_content()
                    
                    if HAS_BS4:
                        # Use BeautifulSoup for better HTML parsing
                        soup = BeautifulSoup(content, 'html.parser')
                        
                        # Remove script and style elements
                        for script in soup(['script', 'style']):
                            script.decompose()
                        
                        text = soup.get_text(separator='\n')
                    else:
                        # Basic HTML stripping without BS4
                        text = self._strip_html_basic(content.decode('utf-8', errors='ignore'))
                    
                    if text.strip():
                        text_parts.append(text)
            
            text = '\n\n'.join(text_parts)
            text = self._clean_epub_text(text)
            
            if not text.strip():
                raise FileReadError(f"No text could be extracted from EPUB: {file_path}")
            
            logger.info(f"Extracted {len(text_parts)} chapters from EPUB")
            return text
            
        except Exception as e:
            if isinstance(e, (FileReadError, UnsupportedFormatError)):
                raise
            raise FileReadError(f"Error reading EPUB {file_path}: {e}")
    
    def _strip_html_basic(self, html: str) -> str:
        """Basic HTML tag stripping without BeautifulSoup."""
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', html)
        # Decode common HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        text = text.replace('&#39;', "'")
        return text
    
    def _clean_epub_text(self, text: str) -> str:
        """Clean up EPUB extraction artifacts."""
        # Normalize whitespace
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Fix multiple newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove leading/trailing whitespace from lines
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)
        
        return text.strip()


class FileReaderFactory:
    """
    Factory for creating appropriate file readers.
    
    Example:
        >>> reader = FileReaderFactory.get_reader("book.pdf")
        >>> text = reader.read(Path("book.pdf"))
    """
    
    _readers: Dict[str, Type[BaseReader]] = {}
    
    @classmethod
    def register_reader(cls, reader_class: Type[BaseReader]) -> None:
        """Register a reader class for its supported extensions."""
        for ext in reader_class.supported_extensions:
            cls._readers[ext.lower()] = reader_class
    
    @classmethod
    def get_reader(cls, file_path: str) -> BaseReader:
        """
        Get appropriate reader for a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Appropriate reader instance
            
        Raises:
            UnsupportedFormatError: If format is not supported
        """
        path = Path(file_path)
        ext = path.suffix.lower()
        
        if ext in cls._readers:
            return cls._readers[ext]()
        
        # Check if it might be a supported format with missing dependency
        if ext == '.pdf' and not HAS_PYPDF:
            raise UnsupportedFormatError(
                "PDF support requires pypdf. Install with: pip install pypdf"
            )
        if ext == '.epub' and not HAS_EBOOKLIB:
            raise UnsupportedFormatError(
                "EPUB support requires ebooklib. Install with: pip install ebooklib"
            )
        
        raise UnsupportedFormatError(
            f"Unsupported file format: {ext}. "
            f"Supported formats: {list(cls._readers.keys())}"
        )
    
    @classmethod
    def get_supported_extensions(cls) -> list:
        """Get list of all supported file extensions."""
        return list(cls._readers.keys())
    
    @classmethod
    def is_supported(cls, file_path: str) -> bool:
        """Check if a file format is supported."""
        ext = Path(file_path).suffix.lower()
        return ext in cls._readers


# Register default readers
FileReaderFactory.register_reader(TextReader)
if HAS_PYPDF:
    FileReaderFactory.register_reader(PDFReader)
if HAS_EBOOKLIB:
    FileReaderFactory.register_reader(EPUBReader)


def read_file(file_path: str, encoding: Optional[str] = None) -> str:
    """
    Read text content from a file of any supported format.
    
    This is the main entry point for reading files. It automatically
    detects the file format and uses the appropriate reader.
    
    Args:
        file_path: Path to the file
        encoding: Optional encoding for text files
        
    Returns:
        Extracted text content
        
    Example:
        >>> text = read_file("book.pdf")
        >>> print(f"Extracted {len(text)} characters")
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileReadError(f"File not found: {file_path}")
    
    reader = FileReaderFactory.get_reader(file_path)
    
    # Pass encoding if it's a text reader
    if isinstance(reader, TextReader) and encoding:
        reader.encoding = encoding
    
    return reader.read(path)


def get_supported_formats() -> Dict[str, bool]:
    """
    Get supported formats and their availability status.
    
    Returns:
        Dictionary mapping format names to availability
    """
    return {
        'text': True,
        'pdf': HAS_PYPDF,
        'epub': HAS_EBOOKLIB,
    }
