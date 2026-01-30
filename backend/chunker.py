"""
Text Chunker with Overlap
Splits documents into smaller chunks for embedding and retrieval
"""

import logging
import re
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class TextChunker:
    """Split text into overlapping chunks"""
    
    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 100,
        separator: str = "\n\n"
    ):
        """
        Initialize text chunker
        
        Args:
            chunk_size: Maximum characters per chunk
            chunk_overlap: Number of overlapping characters between chunks
            separator: Primary separator for splitting text
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separator = separator
    
    def chunk(self, text: str) -> List[Dict[str, Any]]:
        """
        Split text into chunks with overlap
        
        Args:
            text: Text to split
            
        Returns:
            List of chunks with metadata
        """
        if not text or len(text.strip()) == 0:
            return []
        
        logger.info(f"Chunking text of length {len(text)}")
        
        # Extract page information if present
        page_pattern = r'\[PAGE (\d+)\]'
        
        chunks = []
        current_page = 1
        
        # Split by pages first if available
        page_splits = re.split(page_pattern, text)
        
        if len(page_splits) > 1:
            # Text has page markers
            for i in range(1, len(page_splits), 2):
                page_num = int(page_splits[i])
                page_text = page_splits[i + 1] if i + 1 < len(page_splits) else ""
                
                # Chunk each page
                page_chunks = self._split_text(page_text.strip())
                
                for chunk_text in page_chunks:
                    chunks.append({
                        'text': chunk_text,
                        'metadata': {
                            'page': page_num,
                            'char_count': len(chunk_text)
                        }
                    })
        else:
            # No page markers, chunk entire text
            text_chunks = self._split_text(text)
            
            for i, chunk_text in enumerate(text_chunks):
                chunks.append({
                    'text': chunk_text,
                    'metadata': {
                        'page': 1,
                        'char_count': len(chunk_text),
                        'chunk_index': i
                    }
                })
        
        logger.info(f"Created {len(chunks)} chunks")
        return chunks
    
    def _split_text(self, text: str) -> List[str]:
        """
        Split text into chunks with overlap
        
        Args:
            text: Text to split
            
        Returns:
            List of text chunks
        """
        if len(text) <= self.chunk_size:
            return [text] if text.strip() else []
        
        chunks = []
        start = 0
        
        while start < len(text):
            # Calculate end position
            end = start + self.chunk_size
            
            # If not at the end, try to break at a sentence or paragraph
            if end < len(text):
                # Look for good break points
                break_points = [
                    text.rfind('\n\n', start, end),
                    text.rfind('\n', start, end),
                    text.rfind('. ', start, end),
                    text.rfind('! ', start, end),
                    text.rfind('? ', start, end),
                ]
                
                # Use the best available break point
                for bp in break_points:
                    if bp > start:
                        end = bp + 1
                        break
            
            # Extract chunk
            chunk = text[start:end].strip()
            
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            start = end - self.chunk_overlap
            
            # Ensure we make progress
            if start <= chunks[-1:][0][:self.chunk_overlap] if chunks else 0:
                start = end
        
        return chunks
