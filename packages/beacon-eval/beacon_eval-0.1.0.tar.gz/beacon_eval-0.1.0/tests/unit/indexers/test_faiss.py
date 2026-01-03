"""Tests for Faiss vector index."""

import numpy as np
import pytest

from beacon.indexers import FaissIndex
from beacon.models import Chunk


@pytest.fixture
def index_chunks() -> list[Chunk]:
    """Create sample chunks for indexing tests."""
    return [
        Chunk(
            text="First chunk about machine learning",
            doc_id="doc1",
            chunk_id="doc1_chunk_0",
            start_char=0,
            end_char=35,
            token_count=5,
        ),
        Chunk(
            text="Second chunk about deep learning",
            doc_id="doc1",
            chunk_id="doc1_chunk_1",
            start_char=36,
            end_char=68,
            token_count=5,
        ),
        Chunk(
            text="Third chunk about natural language",
            doc_id="doc2",
            chunk_id="doc2_chunk_0",
            start_char=0,
            end_char=34,
            token_count=5,
        ),
    ]


@pytest.fixture
def index_embeddings() -> np.ndarray:
    """Create sample embeddings for testing."""
    # Create 3 embeddings of dimension 8
    np.random.seed(42)
    embeddings = np.random.randn(3, 8).astype(np.float32)
    return embeddings


class TestFaissIndex:
    """Tests for FaissIndex class."""

    def test_init(self) -> None:
        """Test index initialization."""
        index = FaissIndex(dimension=128)
        assert index.dimension == 128
        assert index.index_type == "flat"
        assert index.metric == "cosine"
        assert index.num_chunks == 0

    def test_init_custom_params(self) -> None:
        """Test index initialization with custom parameters."""
        index = FaissIndex(dimension=256, index_type="flat", metric="l2")
        assert index.dimension == 256
        assert index.metric == "l2"

    def test_add_chunks(
        self,
        index_chunks: list[Chunk],
        index_embeddings: np.ndarray,
    ) -> None:
        """Test adding chunks to index."""
        index = FaissIndex(dimension=8)
        index.add(index_chunks, index_embeddings)
        assert index.num_chunks == 3

    def test_add_mismatched_lengths(
        self,
        index_chunks: list[Chunk],
    ) -> None:
        """Test error when chunks and embeddings have different lengths."""
        index = FaissIndex(dimension=8)
        embeddings = np.random.randn(2, 8).astype(np.float32)  # Wrong number

        with pytest.raises(ValueError, match="must match"):
            index.add(index_chunks, embeddings)

    def test_search(
        self,
        index_chunks: list[Chunk],
        index_embeddings: np.ndarray,
    ) -> None:
        """Test searching the index."""
        index = FaissIndex(dimension=8)
        index.add(index_chunks, index_embeddings)

        query_embedding = index_embeddings[0]  # Use first chunk's embedding
        results, latency = index.search(query_embedding, top_k=2)

        assert len(results) == 2
        assert latency >= 0
        # First result should be the most similar
        assert results[0].rank == 1
        assert results[1].rank == 2

    def test_search_returns_scores(
        self,
        index_chunks: list[Chunk],
        index_embeddings: np.ndarray,
    ) -> None:
        """Test that search returns scores."""
        index = FaissIndex(dimension=8)
        index.add(index_chunks, index_embeddings)

        query_embedding = index_embeddings[0]
        results, _ = index.search(query_embedding, top_k=3)

        for result in results:
            assert isinstance(result.score, float)

    def test_search_empty_index(self) -> None:
        """Test searching empty index returns empty results."""
        index = FaissIndex(dimension=8)
        query_embedding = np.random.randn(8).astype(np.float32)

        results, latency = index.search(query_embedding, top_k=5)
        assert len(results) == 0
        assert latency == 0.0

    def test_search_top_k_larger_than_index(
        self,
        index_chunks: list[Chunk],
        index_embeddings: np.ndarray,
    ) -> None:
        """Test searching with top_k larger than index size."""
        index = FaissIndex(dimension=8)
        index.add(index_chunks, index_embeddings)

        query_embedding = np.random.randn(8).astype(np.float32)
        results, _ = index.search(query_embedding, top_k=100)

        assert len(results) <= 3  # Can't return more than we have

    def test_batch_search(
        self,
        index_chunks: list[Chunk],
        index_embeddings: np.ndarray,
    ) -> None:
        """Test batch search."""
        index = FaissIndex(dimension=8)
        index.add(index_chunks, index_embeddings)

        query_embeddings = index_embeddings[:2]  # Use first two
        results = index.batch_search(query_embeddings, top_k=2)

        assert len(results) == 2
        for result_tuple in results:
            result_list, latency = result_tuple
            assert len(result_list) == 2
            assert latency >= 0

    def test_get_chunk(
        self,
        index_chunks: list[Chunk],
        index_embeddings: np.ndarray,
    ) -> None:
        """Test getting a chunk by ID."""
        index = FaissIndex(dimension=8)
        index.add(index_chunks, index_embeddings)

        chunk = index.get_chunk("doc1_chunk_0")
        assert chunk is not None
        assert chunk.text == "First chunk about machine learning"

    def test_get_chunk_not_found(
        self,
        index_chunks: list[Chunk],
        index_embeddings: np.ndarray,
    ) -> None:
        """Test getting non-existent chunk returns None."""
        index = FaissIndex(dimension=8)
        index.add(index_chunks, index_embeddings)

        chunk = index.get_chunk("nonexistent")
        assert chunk is None

    def test_chunks_property(
        self,
        index_chunks: list[Chunk],
        index_embeddings: np.ndarray,
    ) -> None:
        """Test chunks property returns all chunks."""
        index = FaissIndex(dimension=8)
        index.add(index_chunks, index_embeddings)

        chunks = index.chunks
        assert len(chunks) == 3
        assert chunks[0].chunk_id == "doc1_chunk_0"

    def test_cosine_similarity(
        self,
        index_chunks: list[Chunk],
    ) -> None:
        """Test cosine similarity metric."""
        index = FaissIndex(dimension=4, metric="cosine")

        # Create embeddings where first is very similar to query
        embeddings = np.array([
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
        ], dtype=np.float32)

        index.add(index_chunks, embeddings)

        # Query similar to first embedding
        query = np.array([0.9, 0.1, 0.0, 0.0], dtype=np.float32)
        results, _ = index.search(query, top_k=3)

        # First chunk should be most similar
        assert results[0].chunk_id == "doc1_chunk_0"

    def test_l2_metric(self) -> None:
        """Test L2 distance metric."""
        index = FaissIndex(dimension=4, metric="l2")
        assert index.metric == "l2"

    def test_add_multiple_batches(
        self,
        index_chunks: list[Chunk],
        index_embeddings: np.ndarray,
    ) -> None:
        """Test adding chunks in multiple batches."""
        index = FaissIndex(dimension=8)

        # Add first two
        index.add(index_chunks[:2], index_embeddings[:2])
        assert index.num_chunks == 2

        # Add third
        index.add([index_chunks[2]], index_embeddings[2:3])
        assert index.num_chunks == 3

    def test_retrieval_result_contains_text(
        self,
        index_chunks: list[Chunk],
        index_embeddings: np.ndarray,
    ) -> None:
        """Test that retrieval results contain chunk text."""
        index = FaissIndex(dimension=8)
        index.add(index_chunks, index_embeddings)

        query_embedding = index_embeddings[0]
        results, _ = index.search(query_embedding, top_k=1)

        assert results[0].text != ""
        assert results[0].doc_id in ["doc1", "doc2"]

    def test_retrieval_result_contains_doc_id(
        self,
        index_chunks: list[Chunk],
        index_embeddings: np.ndarray,
    ) -> None:
        """Test that retrieval results contain doc_id."""
        index = FaissIndex(dimension=8)
        index.add(index_chunks, index_embeddings)

        query_embedding = index_embeddings[2]  # Query for doc2
        results, _ = index.search(query_embedding, top_k=1)

        assert results[0].doc_id is not None
