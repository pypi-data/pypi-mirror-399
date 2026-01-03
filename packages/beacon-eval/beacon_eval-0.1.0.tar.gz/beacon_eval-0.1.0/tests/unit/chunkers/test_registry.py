"""Tests for chunker registry."""

import pytest

from beacon.chunkers import get_chunker
from beacon.chunkers.registry import ChunkerRegistry
from beacon.chunkers.fixed import FixedSizeChunker
from beacon.chunkers.sentence import SentenceChunker, ParagraphChunker
from beacon.chunkers.recursive import RecursiveChunker
from beacon.chunkers.semantic import SemanticChunker
from beacon.models import ChunkingStrategy, ChunkingStrategyType


class TestGetChunker:
    """Tests for get_chunker factory function."""

    def test_get_fixed_chunker(self) -> None:
        """Test getting a fixed size chunker."""
        strategy = ChunkingStrategy(
            name="test",
            strategy_type=ChunkingStrategyType.FIXED_SIZE,
        )
        chunker = get_chunker(strategy)
        assert isinstance(chunker, FixedSizeChunker)

    def test_get_sentence_chunker(self) -> None:
        """Test getting a sentence chunker."""
        strategy = ChunkingStrategy(
            name="test",
            strategy_type=ChunkingStrategyType.SENTENCE,
        )
        chunker = get_chunker(strategy)
        assert isinstance(chunker, SentenceChunker)

    def test_get_recursive_chunker(self) -> None:
        """Test getting a recursive chunker."""
        strategy = ChunkingStrategy(
            name="test",
            strategy_type=ChunkingStrategyType.RECURSIVE,
        )
        chunker = get_chunker(strategy)
        assert isinstance(chunker, RecursiveChunker)

    def test_get_paragraph_chunker(self) -> None:
        """Test getting a paragraph chunker."""
        strategy = ChunkingStrategy(
            name="test",
            strategy_type=ChunkingStrategyType.PARAGRAPH,
        )
        chunker = get_chunker(strategy)
        assert isinstance(chunker, ParagraphChunker)

    def test_get_semantic_chunker(self) -> None:
        """Test getting a semantic chunker."""
        strategy = ChunkingStrategy(
            name="test",
            strategy_type=ChunkingStrategyType.SEMANTIC,
        )
        chunker = get_chunker(strategy)
        assert isinstance(chunker, SemanticChunker)


class TestChunkerRegistry:
    """Tests for ChunkerRegistry class."""

    def test_registry_has_all_types(self) -> None:
        """Test that registry has all strategy types."""
        for strategy_type in ChunkingStrategyType:
            strategy = ChunkingStrategy(
                name="test",
                strategy_type=strategy_type,
            )
            # Should not raise
            chunker = get_chunker(strategy)
            assert chunker is not None

    def test_chunker_has_correct_strategy(self) -> None:
        """Test that chunker receives the strategy correctly."""
        strategy = ChunkingStrategy(
            name="custom_name",
            strategy_type=ChunkingStrategyType.FIXED_SIZE,
            chunk_size=256,
            chunk_overlap=32,
        )
        chunker = get_chunker(strategy)
        assert chunker.strategy == strategy
        assert chunker.chunk_size == 256
        assert chunker.chunk_overlap == 32

    def test_list_strategies(self) -> None:
        """Test listing registered strategies."""
        strategies = ChunkerRegistry.list_strategies()
        assert ChunkingStrategyType.FIXED_SIZE in strategies
        assert ChunkingStrategyType.SENTENCE in strategies

    def test_register_custom_chunker(self) -> None:
        """Test registering a custom chunker."""
        # Register a custom chunker for an existing type
        original = ChunkerRegistry.get(ChunkingStrategyType.FIXED_SIZE)
        ChunkerRegistry.register(ChunkingStrategyType.FIXED_SIZE, FixedSizeChunker)
        assert ChunkerRegistry.get(ChunkingStrategyType.FIXED_SIZE) == FixedSizeChunker
        # Restore original
        ChunkerRegistry.register(ChunkingStrategyType.FIXED_SIZE, original)
