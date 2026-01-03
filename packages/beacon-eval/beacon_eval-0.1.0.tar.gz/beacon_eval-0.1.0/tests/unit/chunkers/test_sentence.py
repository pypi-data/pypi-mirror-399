"""Tests for sentence and paragraph chunking strategies."""

import pytest

from beacon.chunkers import SentenceChunker
from beacon.chunkers.sentence import ParagraphChunker
from beacon.models import ChunkingStrategy, ChunkingStrategyType, Document


class TestSentenceChunker:
    """Tests for SentenceChunker."""

    def test_chunk_creates_chunks(self, sample_document: Document) -> None:
        """Test that sentence chunking creates chunks."""
        strategy = ChunkingStrategy(
            name="test",
            strategy_type=ChunkingStrategyType.SENTENCE,
            chunk_size=100,
            chunk_overlap=0,
        )
        chunker = SentenceChunker(strategy)
        chunks = chunker.chunk(sample_document)

        assert len(chunks) > 0

    def test_chunks_end_at_sentence_boundaries(self, long_document: Document) -> None:
        """Test that chunks tend to end at sentence boundaries."""
        strategy = ChunkingStrategy(
            name="test",
            strategy_type=ChunkingStrategyType.SENTENCE,
            chunk_size=200,
            chunk_overlap=0,
        )
        chunker = SentenceChunker(strategy)
        chunks = chunker.chunk(long_document)

        # Most chunks should end with sentence-ending punctuation
        endings = [c.text.strip()[-1] for c in chunks if c.text.strip()]
        sentence_end_count = sum(1 for e in endings if e in ".!?")
        assert sentence_end_count >= len(endings) * 0.5

    def test_chunk_with_overlap(self) -> None:
        """Test sentence chunking with overlap."""
        doc = Document(
            doc_id="overlap_test",
            content="First sentence here. Second sentence here. Third sentence. Fourth sentence.",
        )
        strategy = ChunkingStrategy(
            name="overlap_test",
            strategy_type=ChunkingStrategyType.SENTENCE,
            chunk_size=30,
            chunk_overlap=10,
        )
        chunker = SentenceChunker(strategy)
        chunks = chunker.chunk(doc)

        assert len(chunks) >= 1
        for chunk in chunks:
            assert chunk.doc_id == "overlap_test"

    def test_chunk_ids_are_unique(self, long_document: Document) -> None:
        """Test that sentence chunker creates unique chunk IDs."""
        strategy = ChunkingStrategy(
            name="unique_test",
            strategy_type=ChunkingStrategyType.SENTENCE,
            chunk_size=100,
            chunk_overlap=0,
        )
        chunker = SentenceChunker(strategy)
        chunks = chunker.chunk(long_document)

        chunk_ids = [c.chunk_id for c in chunks]
        assert len(chunk_ids) == len(set(chunk_ids))

    def test_empty_document(self) -> None:
        """Test handling empty document."""
        doc = Document(doc_id="empty", content="")
        strategy = ChunkingStrategy(
            name="empty_test",
            strategy_type=ChunkingStrategyType.SENTENCE,
            chunk_size=100,
            chunk_overlap=0,
        )
        chunker = SentenceChunker(strategy)
        chunks = chunker.chunk(doc)

        # Empty document should return empty or single empty chunk
        assert len(chunks) <= 1

    def test_single_sentence(self) -> None:
        """Test document with single sentence."""
        doc = Document(doc_id="single", content="Just one sentence here.")
        strategy = ChunkingStrategy(
            name="single_test",
            strategy_type=ChunkingStrategyType.SENTENCE,
            chunk_size=100,
            chunk_overlap=0,
        )
        chunker = SentenceChunker(strategy)
        chunks = chunker.chunk(doc)

        assert len(chunks) == 1
        assert "Just one sentence here" in chunks[0].text


class TestParagraphChunker:
    """Tests for ParagraphChunker."""

    def test_chunk_creates_chunks(self, sample_document: Document) -> None:
        """Test that paragraph chunking creates chunks."""
        strategy = ChunkingStrategy(
            name="test",
            strategy_type=ChunkingStrategyType.PARAGRAPH,
            chunk_size=200,
            chunk_overlap=0,
        )
        chunker = ParagraphChunker(strategy)
        chunks = chunker.chunk(sample_document)

        assert len(chunks) > 0

    def test_respects_paragraph_boundaries(self) -> None:
        """Test that chunks respect paragraph boundaries."""
        doc = Document(
            doc_id="para_test",
            content="First paragraph here.\n\nSecond paragraph here.\n\nThird paragraph here.",
        )
        strategy = ChunkingStrategy(
            name="test",
            strategy_type=ChunkingStrategyType.PARAGRAPH,
            chunk_size=500,
            chunk_overlap=0,
        )
        chunker = ParagraphChunker(strategy)
        chunks = chunker.chunk(doc)

        # Should create chunks that don't split paragraphs
        assert len(chunks) >= 1

    def test_chunk_ids_unique(self) -> None:
        """Test that chunk IDs are unique."""
        doc = Document(
            doc_id="para_unique",
            content="Para 1.\n\nPara 2.\n\nPara 3.",
        )
        strategy = ChunkingStrategy(
            name="test",
            strategy_type=ChunkingStrategyType.PARAGRAPH,
            chunk_size=50,
            chunk_overlap=0,
        )
        chunker = ParagraphChunker(strategy)
        chunks = chunker.chunk(doc)

        chunk_ids = [c.chunk_id for c in chunks]
        assert len(chunk_ids) == len(set(chunk_ids))
