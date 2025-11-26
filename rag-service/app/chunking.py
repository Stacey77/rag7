"""
Advanced document chunking strategies for RAG.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import re


@dataclass
class Chunk:
    """Represents a text chunk with metadata."""
    text: str
    metadata: Dict[str, Any]
    chunk_id: int
    start_char: int
    end_char: int


class DocumentChunker:
    """Smart document chunking with multiple strategies."""
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separator: str = "\n\n"
    ):
        """
        Initialize the chunker.
        
        Args:
            chunk_size: Target size of each chunk in characters
            chunk_overlap: Number of characters to overlap between chunks
            separator: Primary separator for splitting
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separator = separator
    
    def chunk_by_character(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Chunk]:
        """
        Chunk text by character count with overlap.
        
        Args:
            text: Input text to chunk
            metadata: Optional metadata to attach to chunks
            
        Returns:
            List of Chunk objects
        """
        if not text:
            return []
        
        chunks = []
        metadata = metadata or {}
        
        start = 0
        chunk_id = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # If not at the end, try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings within the last 20% of chunk
                search_start = max(start, end - int(self.chunk_size * 0.2))
                sentence_end = self._find_sentence_end(text, search_start, end)
                if sentence_end > start:
                    end = sentence_end
            
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append(Chunk(
                    text=chunk_text,
                    metadata={**metadata, "chunk_id": chunk_id},
                    chunk_id=chunk_id,
                    start_char=start,
                    end_char=end
                ))
                chunk_id += 1
            
            # Move start with overlap
            start = end - self.chunk_overlap
            
            # Prevent infinite loop
            if start >= len(text) - self.chunk_overlap:
                break
        
        return chunks
    
    def chunk_by_separator(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Chunk]:
        """
        Chunk text by separator (e.g., paragraphs).
        
        Args:
            text: Input text to chunk
            metadata: Optional metadata to attach to chunks
            
        Returns:
            List of Chunk objects
        """
        if not text:
            return []
        
        # Split by separator
        sections = text.split(self.separator)
        chunks = []
        metadata = metadata or {}
        
        current_chunk = ""
        chunk_id = 0
        start_char = 0
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
            
            # If adding this section exceeds chunk size, save current chunk
            if current_chunk and len(current_chunk) + len(section) > self.chunk_size:
                end_char = start_char + len(current_chunk)
                chunks.append(Chunk(
                    text=current_chunk.strip(),
                    metadata={**metadata, "chunk_id": chunk_id},
                    chunk_id=chunk_id,
                    start_char=start_char,
                    end_char=end_char
                ))
                chunk_id += 1
                
                # Start new chunk with overlap
                overlap_text = self._get_overlap_text(current_chunk)
                current_chunk = overlap_text + " " + section
                start_char = end_char - len(overlap_text)
            else:
                if current_chunk:
                    current_chunk += " " + section
                else:
                    current_chunk = section
        
        # Add final chunk
        if current_chunk:
            chunks.append(Chunk(
                text=current_chunk.strip(),
                metadata={**metadata, "chunk_id": chunk_id},
                chunk_id=chunk_id,
                start_char=start_char,
                end_char=start_char + len(current_chunk)
            ))
        
        return chunks
    
    def chunk_by_sentence(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Chunk]:
        """
        Chunk text by sentences, grouping to reach target size.
        
        Args:
            text: Input text to chunk
            metadata: Optional metadata to attach to chunks
            
        Returns:
            List of Chunk objects
        """
        if not text:
            return []
        
        # Split into sentences
        sentences = self._split_sentences(text)
        chunks = []
        metadata = metadata or {}
        
        current_chunk = ""
        chunk_id = 0
        start_char = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # If adding this sentence exceeds chunk size significantly, save current chunk
            if current_chunk and len(current_chunk) + len(sentence) > self.chunk_size * 1.2:
                end_char = start_char + len(current_chunk)
                chunks.append(Chunk(
                    text=current_chunk.strip(),
                    metadata={**metadata, "chunk_id": chunk_id},
                    chunk_id=chunk_id,
                    start_char=start_char,
                    end_char=end_char
                ))
                chunk_id += 1
                
                # Start new chunk with overlap
                overlap_text = self._get_overlap_sentences(current_chunk)
                current_chunk = overlap_text + " " + sentence
                start_char = end_char - len(overlap_text)
            else:
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence
        
        # Add final chunk
        if current_chunk:
            chunks.append(Chunk(
                text=current_chunk.strip(),
                metadata={**metadata, "chunk_id": chunk_id},
                chunk_id=chunk_id,
                start_char=start_char,
                end_char=start_char + len(current_chunk)
            ))
        
        return chunks
    
    def _find_sentence_end(self, text: str, start: int, end: int) -> int:
        """Find the nearest sentence ending."""
        sentence_enders = ['. ', '! ', '? ', '.\n', '!\n', '?\n']
        
        # Search backwards from end
        for i in range(end - 1, start, -1):
            for ender in sentence_enders:
                if text[i:i+len(ender)] == ender:
                    return i + len(ender)
        
        return end
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitter - could be improved with nltk
        pattern = r'(?<=[.!?])\s+'
        sentences = re.split(pattern, text)
        return [s for s in sentences if s.strip()]
    
    def _get_overlap_text(self, text: str) -> str:
        """Get overlap text from end of chunk."""
        if len(text) <= self.chunk_overlap:
            return text
        return text[-self.chunk_overlap:]
    
    def _get_overlap_sentences(self, text: str) -> str:
        """Get last few sentences for overlap."""
        sentences = self._split_sentences(text)
        overlap = ""
        for sentence in reversed(sentences):
            if len(overlap) + len(sentence) > self.chunk_overlap:
                break
            overlap = sentence + " " + overlap
        return overlap.strip()


def chunk_document(
    text: str,
    strategy: str = "character",
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    metadata: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Chunk a document using the specified strategy.
    
    Args:
        text: Input text to chunk
        strategy: Chunking strategy ("character", "separator", "sentence")
        chunk_size: Target chunk size in characters
        chunk_overlap: Overlap between chunks
        metadata: Optional metadata to attach to chunks
        
    Returns:
        List of chunk dictionaries
    """
    chunker = DocumentChunker(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    
    if strategy == "character":
        chunks = chunker.chunk_by_character(text, metadata)
    elif strategy == "separator":
        chunks = chunker.chunk_by_separator(text, metadata)
    elif strategy == "sentence":
        chunks = chunker.chunk_by_sentence(text, metadata)
    else:
        raise ValueError(f"Unknown chunking strategy: {strategy}")
    
    return [
        {
            "text": chunk.text,
            "metadata": chunk.metadata,
            "chunk_id": chunk.chunk_id,
            "start_char": chunk.start_char,
            "end_char": chunk.end_char
        }
        for chunk in chunks
    ]
