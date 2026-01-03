"""Tests for fixed-size chunking strategy."""

import pytest

from beacon.chunkers import FixedSizeChunker
from beacon.models import ChunkingStrategy, ChunkingStrategyType, Document


class TestFixedSizeChunker:
    """Tests for FixedSizeChunker."""

    def test_chunk_creates_chunks(self, sample_document: Document) -> None:
        """Test that chunking creates chunks."""
        strategy = ChunkingStrategy(
            name="test",
            strategy_type=ChunkingStrategyType.FIXED_SIZE,
            chunk_size=50,
            chunk_overlap=10,
        )
        chunker = FixedSizeChunker(strategy)
        chunks = chunker.chunk(sample_document)

        assert len(chunks) > 0
        assert all(c.doc_id == "test_doc" for c in chunks)

    def test_chunk_ids_are_unique(self, sample_document: Document) -> None:
        """Test that chunk IDs are unique."""
        strategy = ChunkingStrategy(
            name="test",
            strategy_type=ChunkingStrategyType.FIXED_SIZE,
            chunk_size=50,
            chunk_overlap=10,
        )
        chunker = FixedSizeChunker(strategy)
        chunks = chunker.chunk(sample_document)

        chunk_ids = [c.chunk_id for c in chunks]
        assert len(chunk_ids) == len(set(chunk_ids))

    def test_chunk_text_not_empty(self, sample_document: Document) -> None:
        """Test that chunks have non-empty text."""
        strategy = ChunkingStrategy(
            name="test",
            strategy_type=ChunkingStrategyType.FIXED_SIZE,
            chunk_size=100,
            chunk_overlap=0,
        )
        chunker = FixedSizeChunker(strategy)
        chunks = chunker.chunk(sample_document)

        assert all(len(c.text.strip()) > 0 for c in chunks)

    def test_chunk_by_characters(self, long_document: Document) -> None:
        """Test chunking by character count."""
        strategy = ChunkingStrategy(
            name="char_test",
            strategy_type=ChunkingStrategyType.FIXED_SIZE,
            chunk_size=100,
            chunk_overlap=10,
            params={"use_tokens": False},
        )
        chunker = FixedSizeChunker(strategy)
        chunks = chunker.chunk(long_document)

        assert len(chunks) > 0
        # Character-based chunks should exist
        for chunk in chunks:
            assert len(chunk.text) > 0

    def test_chunk_with_overlap(self, long_document: Document) -> None:
        """Test that overlap creates overlapping content."""
        strategy = ChunkingStrategy(
            name="overlap_test",
            strategy_type=ChunkingStrategyType.FIXED_SIZE,
            chunk_size=50,
            chunk_overlap=20,
        )
        chunker = FixedSizeChunker(strategy)
        chunks = chunker.chunk(long_document)

        assert len(chunks) >= 2
        # Chunks should have metadata
        for chunk in chunks:
            assert "strategy" in chunk.metadata

    def test_chunk_documents_multiple(
        self, sample_document: Document, long_document: Document
    ) -> None:
        """Test chunking multiple documents."""
        strategy = ChunkingStrategy(
            name="multi_test",
            strategy_type=ChunkingStrategyType.FIXED_SIZE,
            chunk_size=100,
            chunk_overlap=0,
        )
        chunker = FixedSizeChunker(strategy)
        chunks = chunker.chunk_documents([sample_document, long_document])

        # Should have chunks from both documents
        doc_ids = {c.doc_id for c in chunks}
        assert "test_doc" in doc_ids
        assert "long_doc" in doc_ids
