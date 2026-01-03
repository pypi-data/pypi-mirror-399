"""Tests for semantic chunker."""

import numpy as np
import pytest
from unittest.mock import MagicMock

from beacon.chunkers.semantic import SemanticChunker
from beacon.models import ChunkingStrategy, ChunkingStrategyType, Document


@pytest.fixture
def semantic_document() -> Document:
    """Create a sample document for semantic testing."""
    return Document(
        doc_id="test_doc",
        content="This is the first sentence. This is the second sentence. And here is the third one. Finally the fourth sentence.",
    )


@pytest.fixture
def topic_shift_document() -> Document:
    """Create a document with clear topic shifts."""
    return Document(
        doc_id="topic_doc",
        content=(
            "Machine learning is a subset of artificial intelligence. "
            "It enables computers to learn from data. "
            "Deep learning uses neural networks with many layers. "
            "Now let's talk about cooking. "
            "Pasta is a popular Italian dish. "
            "It can be served with various sauces."
        ),
    )


@pytest.fixture
def semantic_strategy() -> ChunkingStrategy:
    """Create a semantic chunking strategy."""
    return ChunkingStrategy(
        name="semantic_test",
        strategy_type=ChunkingStrategyType.SEMANTIC,
        chunk_size=512,
        chunk_overlap=0,
        params={"breakpoint_threshold": 0.5},
    )


class TestSemanticChunkerInit:
    """Tests for SemanticChunker initialization."""

    def test_init_default_params(self, semantic_strategy: ChunkingStrategy) -> None:
        """Test initialization with default parameters."""
        chunker = SemanticChunker(semantic_strategy)
        assert chunker.embedding_model == "all-MiniLM-L6-v2"
        assert chunker.breakpoint_threshold == 0.5

    def test_init_custom_params(self) -> None:
        """Test initialization with custom parameters."""
        strategy = ChunkingStrategy(
            name="custom",
            strategy_type=ChunkingStrategyType.SEMANTIC,
            params={
                "embedding_model": "custom-model",
                "breakpoint_threshold": 0.7,
            },
        )
        chunker = SemanticChunker(strategy)
        assert chunker.embedding_model == "custom-model"
        assert chunker.breakpoint_threshold == 0.7


class TestSemanticChunkerHelpers:
    """Tests for SemanticChunker helper methods."""

    def test_split_into_sentences(self, semantic_strategy: ChunkingStrategy) -> None:
        """Test sentence splitting."""
        chunker = SemanticChunker(semantic_strategy)
        text = "First sentence. Second sentence! Third question? Fourth."
        sentences = chunker._split_into_sentences(text)
        assert len(sentences) == 4
        assert sentences[0] == "First sentence."
        assert sentences[1] == "Second sentence!"

    def test_split_into_sentences_empty(self, semantic_strategy: ChunkingStrategy) -> None:
        """Test sentence splitting with empty text."""
        chunker = SemanticChunker(semantic_strategy)
        sentences = chunker._split_into_sentences("")
        assert len(sentences) == 0

    def test_cosine_similarity(self, semantic_strategy: ChunkingStrategy) -> None:
        """Test cosine similarity calculation."""
        chunker = SemanticChunker(semantic_strategy)

        # Identical vectors should have similarity 1.0
        a = np.array([1.0, 0.0, 0.0])
        b = np.array([1.0, 0.0, 0.0])
        assert chunker._cosine_similarity(a, b) == pytest.approx(1.0)

        # Orthogonal vectors should have similarity 0.0
        a = np.array([1.0, 0.0, 0.0])
        b = np.array([0.0, 1.0, 0.0])
        assert chunker._cosine_similarity(a, b) == pytest.approx(0.0)

    def test_cosine_similarity_zero_vector(self, semantic_strategy: ChunkingStrategy) -> None:
        """Test cosine similarity with zero vector."""
        chunker = SemanticChunker(semantic_strategy)
        a = np.array([0.0, 0.0, 0.0])
        b = np.array([1.0, 0.0, 0.0])
        assert chunker._cosine_similarity(a, b) == 0.0

    def test_find_breakpoints(self, semantic_strategy: ChunkingStrategy) -> None:
        """Test breakpoint finding."""
        chunker = SemanticChunker(semantic_strategy)

        # Create embeddings where there's a clear shift
        embeddings = np.array([
            [1.0, 0.0, 0.0],
            [0.9, 0.1, 0.0],  # Similar to first
            [0.0, 1.0, 0.0],  # Different - should be breakpoint
            [0.0, 0.9, 0.1],  # Similar to third
        ])

        breakpoints = chunker._find_breakpoints(embeddings)
        # Should find a breakpoint between sentences 2 and 3
        assert len(breakpoints) > 0

    def test_find_breakpoints_empty(self, semantic_strategy: ChunkingStrategy) -> None:
        """Test breakpoint finding with no embeddings."""
        chunker = SemanticChunker(semantic_strategy)
        embeddings = np.array([])
        breakpoints = chunker._find_breakpoints(embeddings.reshape(0, 3))
        assert breakpoints == []


class TestSemanticChunkerChunk:
    """Tests for SemanticChunker.chunk method."""

    def test_chunk_single_sentence(
        self,
        semantic_strategy: ChunkingStrategy,
    ) -> None:
        """Test chunking document with single sentence."""
        chunker = SemanticChunker(semantic_strategy)
        doc = Document(doc_id="single", content="Just one sentence.")

        chunks = chunker.chunk(doc)
        assert len(chunks) == 1
        assert chunks[0].text == "Just one sentence."

    def test_chunk_with_mock_model(
        self,
        semantic_strategy: ChunkingStrategy,
        semantic_document: Document,
    ) -> None:
        """Test chunking with mocked embedding model."""
        chunker = SemanticChunker(semantic_strategy)

        # Create mock model that returns embeddings
        mock_model = MagicMock()
        # Return embeddings that create a clear breakpoint
        mock_model.encode.return_value = np.array([
            [1.0, 0.0, 0.0],
            [0.9, 0.1, 0.0],
            [0.0, 1.0, 0.0],  # Topic shift
            [0.0, 0.9, 0.1],
        ])
        chunker._model = mock_model

        chunks = chunker.chunk(semantic_document)
        assert len(chunks) >= 1
        mock_model.encode.assert_called_once()

    def test_chunk_creates_valid_chunks(
        self,
        semantic_strategy: ChunkingStrategy,
        semantic_document: Document,
    ) -> None:
        """Test that chunks have valid structure."""
        chunker = SemanticChunker(semantic_strategy)

        mock_model = MagicMock()
        mock_model.encode.return_value = np.array([
            [1.0, 0.0, 0.0],
            [0.9, 0.1, 0.0],
            [0.8, 0.2, 0.0],
            [0.7, 0.3, 0.0],
        ])
        chunker._model = mock_model

        chunks = chunker.chunk(semantic_document)

        for chunk in chunks:
            assert chunk.doc_id == "test_doc"
            assert chunk.text != ""
            assert chunk.chunk_id.startswith("test_doc_chunk_")


class TestSemanticChunkerCreateChunks:
    """Tests for chunk creation from breakpoints."""

    def test_create_chunks_from_breakpoints(
        self,
        semantic_strategy: ChunkingStrategy,
    ) -> None:
        """Test creating chunks from breakpoints."""
        chunker = SemanticChunker(semantic_strategy)
        sentences = ["First.", "Second.", "Third.", "Fourth."]
        breakpoints = [2]  # Split after second sentence
        original_text = "First. Second. Third. Fourth."

        chunks = chunker._create_chunks_from_breakpoints(
            sentences, breakpoints, "doc1", original_text
        )

        assert len(chunks) == 2
        assert "First." in chunks[0].text
        assert "Third." in chunks[1].text

    def test_create_chunks_no_breakpoints(
        self,
        semantic_strategy: ChunkingStrategy,
    ) -> None:
        """Test creating chunks with no breakpoints."""
        chunker = SemanticChunker(semantic_strategy)
        sentences = ["First.", "Second."]
        breakpoints = []
        original_text = "First. Second."

        chunks = chunker._create_chunks_from_breakpoints(
            sentences, breakpoints, "doc1", original_text
        )

        assert len(chunks) == 1
        assert "First." in chunks[0].text
        assert "Second." in chunks[0].text
