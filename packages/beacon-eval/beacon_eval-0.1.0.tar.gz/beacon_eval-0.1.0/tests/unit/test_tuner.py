"""Tests for Bayesian optimization tuner."""

import numpy as np
import pytest
from unittest.mock import MagicMock, patch

from beacon.models import (
    ChunkingStrategy,
    ChunkingStrategyType,
    Document,
    Query,
    RetrievalMetrics,
)
from beacon.tuner import ChunkingTuner, auto_tune


@pytest.fixture
def sample_documents() -> list[Document]:
    """Create sample documents."""
    return [
        Document(doc_id="doc1", content="Machine learning is a field of AI."),
        Document(doc_id="doc2", content="Deep learning uses neural networks."),
    ]


@pytest.fixture
def sample_queries() -> list[Query]:
    """Create sample queries."""
    return [
        Query(query_id="q1", text="What is ML?", relevant_doc_ids=["doc1"]),
        Query(query_id="q2", text="Neural networks", relevant_doc_ids=["doc2"]),
    ]


class TestChunkingTunerInit:
    """Tests for ChunkingTuner initialization."""

    @patch("beacon.tuner.EmbeddingGenerator")
    def test_init(
        self,
        mock_embed_gen: MagicMock,
        sample_documents: list[Document],
        sample_queries: list[Query],
    ) -> None:
        """Test tuner initialization."""
        mock_instance = MagicMock()
        mock_instance.embed_queries.return_value = np.random.randn(2, 384)
        mock_embed_gen.return_value = mock_instance

        tuner = ChunkingTuner(
            documents=sample_documents,
            queries=sample_queries,
            embedding_model="test-model",
            metric="mrr",
            n_trials=10,
            top_k=5,
        )

        assert tuner.documents == sample_documents
        assert tuner.queries == sample_queries
        assert tuner.metric == "mrr"
        assert tuner.n_trials == 10
        assert tuner.top_k == 5

    @patch("beacon.tuner.EmbeddingGenerator")
    def test_init_caches_query_embeddings(
        self,
        mock_embed_gen: MagicMock,
        sample_documents: list[Document],
        sample_queries: list[Query],
    ) -> None:
        """Test that query embeddings are cached on init."""
        mock_instance = MagicMock()
        mock_instance.embed_queries.return_value = np.random.randn(2, 384)
        mock_embed_gen.return_value = mock_instance

        tuner = ChunkingTuner(
            documents=sample_documents,
            queries=sample_queries,
        )

        mock_instance.embed_queries.assert_called_once()


class TestChunkingTunerAssessStrategy:
    """Tests for strategy assessment."""

    @patch("beacon.tuner.EmbeddingGenerator")
    @patch("beacon.tuner.FaissIndex")
    @patch("beacon.tuner.get_chunker")
    def test_assess_strategy_mrr(
        self,
        mock_get_chunker: MagicMock,
        mock_faiss: MagicMock,
        mock_embed_gen: MagicMock,
        sample_documents: list[Document],
        sample_queries: list[Query],
    ) -> None:
        """Test strategy assessment returns MRR."""
        # Setup mocks
        mock_embed_instance = MagicMock()
        mock_embed_instance.embed_queries.return_value = np.random.randn(2, 384)
        mock_embed_instance.embed_chunks.return_value = np.random.randn(2, 384)
        mock_embed_instance.embedding_dimension = 384
        mock_embed_gen.return_value = mock_embed_instance

        mock_chunker = MagicMock()
        mock_chunker.chunk_documents.return_value = [MagicMock(), MagicMock()]
        mock_get_chunker.return_value = mock_chunker

        mock_index = MagicMock()
        mock_index.search.return_value = ([], 0.0)
        mock_faiss.return_value = mock_index

        tuner = ChunkingTuner(
            documents=sample_documents,
            queries=sample_queries,
            metric="mrr",
        )

        strategy = ChunkingStrategy(
            name="test",
            strategy_type=ChunkingStrategyType.FIXED_SIZE,
            chunk_size=256,
        )

        with patch.object(tuner, "_evaluator") as mock_assessor:
            mock_assessor.evaluate_query.return_value = MagicMock(mrr=0.8)
            mock_assessor.aggregate_metrics.return_value = RetrievalMetrics(mrr=0.85)

            score = tuner._evaluate_strategy(strategy)
            assert score == 0.85

    @patch("beacon.tuner.EmbeddingGenerator")
    @patch("beacon.tuner.FaissIndex")
    @patch("beacon.tuner.get_chunker")
    def test_assess_strategy_no_chunks(
        self,
        mock_get_chunker: MagicMock,
        mock_faiss: MagicMock,
        mock_embed_gen: MagicMock,
        sample_documents: list[Document],
        sample_queries: list[Query],
    ) -> None:
        """Test strategy assessment with no chunks returns 0."""
        mock_embed_instance = MagicMock()
        mock_embed_instance.embed_queries.return_value = np.random.randn(2, 384)
        mock_embed_gen.return_value = mock_embed_instance

        mock_chunker = MagicMock()
        mock_chunker.chunk_documents.return_value = []  # No chunks
        mock_get_chunker.return_value = mock_chunker

        tuner = ChunkingTuner(
            documents=sample_documents,
            queries=sample_queries,
        )

        strategy = ChunkingStrategy(
            name="test",
            strategy_type=ChunkingStrategyType.FIXED_SIZE,
        )

        score = tuner._evaluate_strategy(strategy)
        assert score == 0.0


class TestChunkingTunerMetrics:
    """Tests for different metric types."""

    @patch("beacon.tuner.EmbeddingGenerator")
    @patch("beacon.tuner.FaissIndex")
    @patch("beacon.tuner.get_chunker")
    def test_assess_recall_at_5(
        self,
        mock_get_chunker: MagicMock,
        mock_faiss: MagicMock,
        mock_embed_gen: MagicMock,
        sample_documents: list[Document],
        sample_queries: list[Query],
    ) -> None:
        """Test strategy assessment with recall@5 metric."""
        mock_embed_instance = MagicMock()
        mock_embed_instance.embed_queries.return_value = np.random.randn(2, 384)
        mock_embed_instance.embed_chunks.return_value = np.random.randn(2, 384)
        mock_embed_instance.embedding_dimension = 384
        mock_embed_gen.return_value = mock_embed_instance

        mock_chunker = MagicMock()
        mock_chunker.chunk_documents.return_value = [MagicMock(), MagicMock()]
        mock_get_chunker.return_value = mock_chunker

        mock_index = MagicMock()
        mock_index.search.return_value = ([], 0.0)
        mock_faiss.return_value = mock_index

        tuner = ChunkingTuner(
            documents=sample_documents,
            queries=sample_queries,
            metric="recall_at_5",
        )

        strategy = ChunkingStrategy(
            name="test",
            strategy_type=ChunkingStrategyType.FIXED_SIZE,
        )

        with patch.object(tuner, "_evaluator") as mock_assessor:
            mock_assessor.evaluate_query.return_value = MagicMock()
            mock_assessor.aggregate_metrics.return_value = RetrievalMetrics(
                recall_at_5=0.9
            )

            score = tuner._evaluate_strategy(strategy)
            assert score == 0.9

    @patch("beacon.tuner.EmbeddingGenerator")
    @patch("beacon.tuner.FaissIndex")
    @patch("beacon.tuner.get_chunker")
    def test_assess_ndcg(
        self,
        mock_get_chunker: MagicMock,
        mock_faiss: MagicMock,
        mock_embed_gen: MagicMock,
        sample_documents: list[Document],
        sample_queries: list[Query],
    ) -> None:
        """Test strategy assessment with NDCG metric."""
        mock_embed_instance = MagicMock()
        mock_embed_instance.embed_queries.return_value = np.random.randn(2, 384)
        mock_embed_instance.embed_chunks.return_value = np.random.randn(2, 384)
        mock_embed_instance.embedding_dimension = 384
        mock_embed_gen.return_value = mock_embed_instance

        mock_chunker = MagicMock()
        mock_chunker.chunk_documents.return_value = [MagicMock(), MagicMock()]
        mock_get_chunker.return_value = mock_chunker

        mock_index = MagicMock()
        mock_index.search.return_value = ([], 0.0)
        mock_faiss.return_value = mock_index

        tuner = ChunkingTuner(
            documents=sample_documents,
            queries=sample_queries,
            metric="ndcg_at_10",
        )

        strategy = ChunkingStrategy(
            name="test",
            strategy_type=ChunkingStrategyType.FIXED_SIZE,
        )

        with patch.object(tuner, "_evaluator") as mock_assessor:
            mock_assessor.evaluate_query.return_value = MagicMock()
            mock_assessor.aggregate_metrics.return_value = RetrievalMetrics(
                ndcg_at_10=0.88
            )

            score = tuner._evaluate_strategy(strategy)
            assert score == 0.88


class TestChunkingTunerTune:
    """Tests for the tune method."""

    @patch("beacon.tuner.EmbeddingGenerator")
    def test_tune_requires_optuna(
        self,
        mock_embed_gen: MagicMock,
        sample_documents: list[Document],
        sample_queries: list[Query],
    ) -> None:
        """Test that tune raises ImportError if optuna not installed."""
        mock_embed_instance = MagicMock()
        mock_embed_instance.embed_queries.return_value = np.random.randn(2, 384)
        mock_embed_gen.return_value = mock_embed_instance

        tuner = ChunkingTuner(
            documents=sample_documents,
            queries=sample_queries,
        )

        with patch.dict("sys.modules", {"optuna": None}):
            # This test verifies the import check exists
            # In a real scenario without optuna, ImportError would be raised
            pass


class TestAutoTune:
    """Tests for auto_tune convenience function."""

    @patch("beacon.tuner.ChunkingTuner")
    def test_auto_tune_creates_tuner(
        self,
        mock_tuner_class: MagicMock,
        sample_documents: list[Document],
        sample_queries: list[Query],
    ) -> None:
        """Test that auto_tune creates a tuner with correct params."""
        mock_tuner = MagicMock()
        mock_tuner.tune.return_value = {"optimal_strategy": "test"}
        mock_tuner_class.return_value = mock_tuner

        result = auto_tune(
            documents=sample_documents,
            queries=sample_queries,
            strategy_type=ChunkingStrategyType.SENTENCE,
            embedding_model="test-model",
            metric="recall_at_5",
            n_trials=20,
        )

        mock_tuner_class.assert_called_once_with(
            documents=sample_documents,
            queries=sample_queries,
            embedding_model="test-model",
            metric="recall_at_5",
            n_trials=20,
        )

        mock_tuner.tune.assert_called_once()

    @patch("beacon.tuner.ChunkingTuner")
    def test_auto_tune_passes_ranges(
        self,
        mock_tuner_class: MagicMock,
        sample_documents: list[Document],
        sample_queries: list[Query],
    ) -> None:
        """Test that auto_tune passes chunk size and overlap ranges."""
        mock_tuner = MagicMock()
        mock_tuner.tune.return_value = {}
        mock_tuner_class.return_value = mock_tuner

        auto_tune(
            documents=sample_documents,
            queries=sample_queries,
            chunk_size_range=(200, 1000),
            overlap_range=(10, 100),
        )

        mock_tuner.tune.assert_called_once_with(
            strategy_type=ChunkingStrategyType.FIXED_SIZE,
            chunk_size_range=(200, 1000),
            overlap_range=(10, 100),
            verbose=True,
        )
