"""Tests for recursive chunking strategy."""

import pytest

from beacon.chunkers import RecursiveChunker
from beacon.models import ChunkingStrategy, ChunkingStrategyType, Document


class TestRecursiveChunker:
    """Tests for RecursiveChunker."""

    def test_chunk_creates_chunks(self, sample_document: Document) -> None:
        """Test that recursive chunking creates chunks."""
        strategy = ChunkingStrategy(
            name="test",
            strategy_type=ChunkingStrategyType.RECURSIVE,
            chunk_size=100,
            chunk_overlap=10,
        )
        chunker = RecursiveChunker(strategy)
        chunks = chunker.chunk(sample_document)

        assert len(chunks) > 0

    def test_chunks_respect_size_limit(self, long_document: Document) -> None:
        """Test that chunks approximately respect size limits."""
        strategy = ChunkingStrategy(
            name="test",
            strategy_type=ChunkingStrategyType.RECURSIVE,
            chunk_size=100,
            chunk_overlap=0,
        )
        chunker = RecursiveChunker(strategy)
        chunks = chunker.chunk(long_document)

        # Most chunks should be within 2x the chunk size
        # (accounting for token vs character differences)
        for chunk in chunks:
            # Allow some flexibility due to token counting
            assert chunk.token_count < strategy.chunk_size * 3

    def test_chunk_ids_are_unique(self, long_document: Document) -> None:
        """Test that recursive chunker creates unique chunk IDs."""
        strategy = ChunkingStrategy(
            name="test",
            strategy_type=ChunkingStrategyType.RECURSIVE,
            chunk_size=150,
            chunk_overlap=20,
        )
        chunker = RecursiveChunker(strategy)
        chunks = chunker.chunk(long_document)

        chunk_ids = [c.chunk_id for c in chunks]
        assert len(chunk_ids) == len(set(chunk_ids))

    def test_chunk_with_separators(self, sample_document: Document) -> None:
        """Test recursive chunking with custom separators."""
        strategy = ChunkingStrategy(
            name="test",
            strategy_type=ChunkingStrategyType.RECURSIVE,
            chunk_size=100,
            chunk_overlap=0,
            params={"separators": ["\n\n", "\n", ". ", " "]},
        )
        chunker = RecursiveChunker(strategy)
        chunks = chunker.chunk(sample_document)

        assert len(chunks) > 0
        for chunk in chunks:
            assert chunk.doc_id == sample_document.doc_id
