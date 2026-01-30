"""
Document Loader for PDF and TXT files
Extracts text from various document formats
"""

import logging
from pathlib import Path
from typing import Optional
import pdfplumber

logger = logging.getLogger(__name__)


class DocumentLoader:
    """Load and extract text from PDF and TXT files"""
    
    def __init__(self):
        """Initialize document loader"""
        pass
    
    def load(self, file_path: str) -> str:
        """
        Load text from a document file
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Extracted text content
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_ext = file_path.suffix.lower()
        
        if file_ext == '.pdf':
            return self.load_pdf(file_path)
        elif file_ext == '.txt':
            return self.load_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
    
    def load_pdf(self, file_path: Path) -> str:
        """
        Extract text from PDF file
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text
        """
        try:
            logger.info(f"Loading PDF: {file_path}")
            text_content = []
            
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    # Extract text from page
                    page_text = page.extract_text()
                    
                    if page_text:
                        # Add page marker for metadata tracking
                        text_content.append(f"[PAGE {page_num}]\n{page_text}")
            
            full_text = "\n\n".join(text_content)
            logger.info(f"Extracted {len(full_text)} characters from PDF")
            
            return full_text
            
        except Exception as e:
            logger.error(f"Error loading PDF: {e}")
            raise
    
    def load_txt(self, file_path: Path) -> str:
        """
        Load text from TXT file
        
        Args:
            file_path: Path to TXT file
            
        Returns:
            File content
        """
        try:
            logger.info(f"Loading TXT: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            logger.info(f"Loaded {len(text)} characters from TXT")
            return text
            
        except UnicodeDecodeError:
            # Try with different encoding
            logger.warning("UTF-8 failed, trying latin-1 encoding")
            with open(file_path, 'r', encoding='latin-1') as f:
                text = f.read()
            return text
            
        except Exception as e:
            logger.error(f"Error loading TXT: {e}")
            raise
