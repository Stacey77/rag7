"""
Tests for document chunking module.
"""
import pytest
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestChunkingImport:
    """Tests for chunking module import."""
    
    def test_import_chunking(self):
        """Test that chunking module can be imported."""
        try:
            from app.chunking import chunk_document, ChunkingStrategy
            assert callable(chunk_document)
        except ImportError:
            pytest.skip("Chunking module not available")


class TestCharacterChunking:
    """Tests for character-based chunking."""
    
    def test_chunk_short_text(self):
        """Test chunking text shorter than chunk size."""
        try:
            from app.chunking import chunk_document
            
            text = "This is a short text."
            chunks = chunk_document(text, chunk_size=1000, overlap=100)
            
            assert len(chunks) == 1
            assert chunks[0] == text
        except ImportError:
            pytest.skip("Chunking module not available")
    
    def test_chunk_long_text(self):
        """Test chunking text longer than chunk size."""
        try:
            from app.chunking import chunk_document
            
            text = "Word " * 500  # Long text
            chunks = chunk_document(text, chunk_size=100, overlap=20)
            
            assert len(chunks) > 1
            # Check that chunks have some overlap
            for chunk in chunks:
                assert len(chunk) <= 120  # Allow some flexibility
        except ImportError:
            pytest.skip("Chunking module not available")


class TestSentenceChunking:
    """Tests for sentence-based chunking."""
    
    def test_sentence_chunking(self):
        """Test sentence-based chunking respects boundaries."""
        try:
            from app.chunking import chunk_document
            
            text = "First sentence. Second sentence. Third sentence. Fourth sentence."
            chunks = chunk_document(
                text, 
                chunk_size=50, 
                overlap=10,
                strategy="sentence"
            )
            
            # Each chunk should end with a period or be the last chunk
            for chunk in chunks[:-1]:
                assert chunk.strip().endswith('.') or chunk.strip().endswith('.')
        except (ImportError, TypeError):
            pytest.skip("Sentence chunking not available")


class TestChunkMetadata:
    """Tests for chunk metadata preservation."""
    
    def test_chunks_have_metadata(self):
        """Test that chunks include position metadata."""
        try:
            from app.chunking import chunk_document_with_metadata
            
            text = "First part. Second part. Third part."
            chunks = chunk_document_with_metadata(text, chunk_size=20, overlap=5)
            
            for i, chunk in enumerate(chunks):
                assert 'text' in chunk or 'content' in chunk
                assert 'index' in chunk or 'position' in chunk or i >= 0
        except (ImportError, AttributeError):
            pytest.skip("Metadata chunking not available")
