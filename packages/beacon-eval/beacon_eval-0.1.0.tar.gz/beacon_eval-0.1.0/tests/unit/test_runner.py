"""Tests for benchmark runner."""

import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np

from beacon.models import (
    BenchmarkConfig,
    Chunk,
    ChunkingStrategy,
    ChunkingStrategyType,
    Document,
    Query,
    RetrievalResult,
)
from beacon.runner import (
    evaluate_strategy,
    run_benchmark,
    _generate_recommendation,
    _result_to_dict,
    _export_csv,
)


@pytest.fixture
def sample_documents() -> list[Document]:
    """Create sample documents."""
    return [
        Document(doc_id="doc1", content="Machine learning is great."),
        Document(doc_id="doc2", content="Deep learning uses neural networks."),
    ]


@pytest.fixture
def sample_queries() -> list[Query]:
    """Create sample queries."""
    return [
        Query(query_id="q1", text="What is ML?", relevant_doc_ids=["doc1"]),
        Query(query_id="q2", text="Neural networks", relevant_doc_ids=["doc2"]),
    ]


@pytest.fixture
def sample_strategy() -> ChunkingStrategy:
    """Create a sample chunking strategy."""
    return ChunkingStrategy(
        name="test_fixed",
        strategy_type=ChunkingStrategyType.FIXED_SIZE,
        chunk_size=256,
        chunk_overlap=25,
    )


@pytest.fixture
def mock_embedding_generator() -> MagicMock:
    """Create a mock embedding generator."""
    mock = MagicMock()
    mock.embedding_dimension = 384
    mock.embed_chunks.return_value = np.random.randn(2, 384).astype(np.float32)
    mock.embed_queries.return_value = np.random.randn(2, 384).astype(np.float32)
    return mock


@pytest.fixture
def mock_metrics_assessor() -> MagicMock:
    """Create a mock metrics assessor."""
    from beacon.models import QueryResult, RetrievalMetrics

    mock = MagicMock()
    mock.evaluate_query.return_value = QueryResult(
        query_id="q1",
        query_text="test",
        retrieved=[],
        relevant_doc_ids=["doc1"],
        relevant_chunk_ids=[],
        mrr=0.8,
        recall_at_1=0.5,
    )
    mock.aggregate_metrics.return_value = RetrievalMetrics(
        mrr=0.8,
        recall_at_1=0.5,
        recall_at_5=0.9,
        num_queries=2,
        num_chunks=4,
    )
    return mock


class TestGenerateRecommendation:
    """Tests for _generate_recommendation function."""

    def test_strong_recommendation(self) -> None:
        """Test strong recommendation with large margin."""
        from beacon.models import RetrievalMetrics, StrategyResult

        strategy1 = ChunkingStrategy(
            name="best",
            strategy_type=ChunkingStrategyType.FIXED_SIZE,
            chunk_size=256,
        )
        strategy2 = ChunkingStrategy(
            name="worst",
            strategy_type=ChunkingStrategyType.FIXED_SIZE,
            chunk_size=512,
        )

        result1 = StrategyResult(
            strategy=strategy1,
            metrics=RetrievalMetrics(mrr=0.9),
            query_results=[],
            chunks=[],
        )
        result2 = StrategyResult(
            strategy=strategy2,
            metrics=RetrievalMetrics(mrr=0.7),
            query_results=[],
            chunks=[],
        )

        rec = _generate_recommendation([result1, result2], result1)
        assert "strongly" in rec
        assert "best" in rec

    def test_moderate_recommendation(self) -> None:
        """Test moderate recommendation with medium margin."""
        from beacon.models import RetrievalMetrics, StrategyResult

        strategy1 = ChunkingStrategy(
            name="best",
            strategy_type=ChunkingStrategyType.FIXED_SIZE,
            chunk_size=256,
        )
        strategy2 = ChunkingStrategy(
            name="second",
            strategy_type=ChunkingStrategyType.FIXED_SIZE,
            chunk_size=512,
        )

        result1 = StrategyResult(
            strategy=strategy1,
            metrics=RetrievalMetrics(mrr=0.85),
            query_results=[],
            chunks=[],
        )
        result2 = StrategyResult(
            strategy=strategy2,
            metrics=RetrievalMetrics(mrr=0.78),
            query_results=[],
            chunks=[],
        )

        rec = _generate_recommendation([result1, result2], result1)
        assert "moderately" in rec

    def test_slight_recommendation(self) -> None:
        """Test slight recommendation with small margin."""
        from beacon.models import RetrievalMetrics, StrategyResult

        strategy1 = ChunkingStrategy(
            name="best",
            strategy_type=ChunkingStrategyType.FIXED_SIZE,
            chunk_size=256,
        )
        strategy2 = ChunkingStrategy(
            name="almost",
            strategy_type=ChunkingStrategyType.FIXED_SIZE,
            chunk_size=512,
        )

        result1 = StrategyResult(
            strategy=strategy1,
            metrics=RetrievalMetrics(mrr=0.85),
            query_results=[],
            chunks=[],
        )
        result2 = StrategyResult(
            strategy=strategy2,
            metrics=RetrievalMetrics(mrr=0.83),
            query_results=[],
            chunks=[],
        )

        rec = _generate_recommendation([result1, result2], result1)
        assert "slightly" in rec

    def test_small_chunk_size_insight(self) -> None:
        """Test insight for small chunk sizes."""
        from beacon.models import RetrievalMetrics, StrategyResult

        strategy = ChunkingStrategy(
            name="small",
            strategy_type=ChunkingStrategyType.FIXED_SIZE,
            chunk_size=200,
        )
        result = StrategyResult(
            strategy=strategy,
            metrics=RetrievalMetrics(mrr=0.9),
            query_results=[],
            chunks=[],
        )

        rec = _generate_recommendation([result], result)
        assert "Smaller chunk sizes" in rec

    def test_large_chunk_size_insight(self) -> None:
        """Test insight for large chunk sizes."""
        from beacon.models import RetrievalMetrics, StrategyResult

        strategy = ChunkingStrategy(
            name="large",
            strategy_type=ChunkingStrategyType.FIXED_SIZE,
            chunk_size=1024,
        )
        result = StrategyResult(
            strategy=strategy,
            metrics=RetrievalMetrics(mrr=0.9),
            query_results=[],
            chunks=[],
        )

        rec = _generate_recommendation([result], result)
        assert "Larger chunk sizes" in rec


class TestResultToDict:
    """Tests for _result_to_dict function."""

    def test_converts_result(self) -> None:
        """Test converting benchmark result to dict."""
        from beacon.models import BenchmarkResult, RetrievalMetrics, StrategyResult

        strategy = ChunkingStrategy(
            name="test",
            strategy_type=ChunkingStrategyType.FIXED_SIZE,
            chunk_size=256,
            chunk_overlap=25,
        )
        metrics = RetrievalMetrics(mrr=0.85, recall_at_5=0.9)
        strategy_result = StrategyResult(
            strategy=strategy,
            metrics=metrics,
            query_results=[],
            chunks=[],
            embedding_time_ms=100.0,
            indexing_time_ms=50.0,
        )
        config = BenchmarkConfig(
            name="test_bench",
            documents=[Path("doc.txt")],
            queries_file=Path("q.jsonl"),
            strategies=[strategy],
            embedding_model="test-model",
            top_k=5,
        )
        result = BenchmarkResult(
            config=config,
            strategy_results=[strategy_result],
            best_strategy="test",
            recommendation="Use test",
            total_time_ms=1000.0,
        )

        result_dict = _result_to_dict(result)

        assert result_dict["config"]["name"] == "test_bench"
        assert result_dict["config"]["embedding_model"] == "test-model"
        assert result_dict["best_strategy"] == "test"
        assert result_dict["recommendation"] == "Use test"
        assert result_dict["total_time_ms"] == 1000.0
        assert len(result_dict["strategy_results"]) == 1


class TestExportCsv:
    """Tests for _export_csv function."""

    def test_exports_csv(self, tmp_path: Path) -> None:
        """Test CSV export."""
        from beacon.models import BenchmarkResult, RetrievalMetrics, StrategyResult

        strategy = ChunkingStrategy(
            name="test",
            strategy_type=ChunkingStrategyType.FIXED_SIZE,
            chunk_size=256,
            chunk_overlap=25,
        )
        metrics = RetrievalMetrics(
            mrr=0.85,
            recall_at_1=0.7,
            recall_at_5=0.9,
            recall_at_10=0.95,
            ndcg_at_10=0.88,
            avg_latency_ms=5.5,
            num_chunks=100,
        )
        strategy_result = StrategyResult(
            strategy=strategy,
            metrics=metrics,
            query_results=[],
            chunks=[],
        )
        config = BenchmarkConfig(
            name="test",
            documents=[],
            queries_file=Path("q.jsonl"),
            strategies=[strategy],
        )
        result = BenchmarkResult(
            config=config,
            strategy_results=[strategy_result],
            best_strategy="test",
            recommendation="test",
        )

        csv_path = tmp_path / "results.csv"
        _export_csv(result, csv_path)

        assert csv_path.exists()
        content = csv_path.read_text()
        assert "Strategy" in content
        assert "MRR" in content
        assert "test" in content
        assert "0.8500" in content


class TestAssessStrategy:
    """Tests for assess_strategy function."""

    def test_assesses_strategy(
        self,
        sample_documents: list[Document],
        sample_queries: list[Query],
        sample_strategy: ChunkingStrategy,
        mock_embedding_generator: MagicMock,
        mock_metrics_assessor: MagicMock,
    ) -> None:
        """Test assessing a strategy."""
        with patch("beacon.runner.FaissIndex") as MockIndex:
            mock_index = MagicMock()
            mock_index.search.return_value = (
                [
                    RetrievalResult(
                        chunk_id="c1",
                        doc_id="doc1",
                        score=0.9,
                        text="test",
                        rank=1,
                    )
                ],
                5.0,
            )
            MockIndex.return_value = mock_index

            result = evaluate_strategy(
                strategy=sample_strategy,
                documents=sample_documents,
                queries=sample_queries,
                embedding_generator=mock_embedding_generator,
                evaluator=mock_metrics_assessor,
                top_k=10,
                verbose=False,
            )

            assert result.strategy == sample_strategy
            assert result.metrics is not None
            assert len(result.query_results) == 2


class TestRunBenchmark:
    """Integration tests for run_benchmark function."""

    def test_raises_on_no_documents(self, tmp_path: Path) -> None:
        """Test error when document file not found."""
        queries_file = tmp_path / "queries.jsonl"
        queries_file.write_text('{"query": "test"}')

        config = BenchmarkConfig(
            name="test",
            documents=[tmp_path / "nonexistent"],
            queries_file=queries_file,
            strategies=[
                ChunkingStrategy(
                    name="test",
                    strategy_type=ChunkingStrategyType.FIXED_SIZE,
                )
            ],
        )

        with pytest.raises(FileNotFoundError, match="Document not found"):
            run_benchmark(config, verbose=False)

    def test_raises_on_no_queries(self, tmp_path: Path) -> None:
        """Test error when no queries found."""
        doc_file = tmp_path / "doc.txt"
        doc_file.write_text("Document content")
        queries_file = tmp_path / "queries.jsonl"
        queries_file.write_text("")  # Empty file

        config = BenchmarkConfig(
            name="test",
            documents=[doc_file],
            queries_file=queries_file,
            strategies=[
                ChunkingStrategy(
                    name="test",
                    strategy_type=ChunkingStrategyType.FIXED_SIZE,
                )
            ],
        )

        with pytest.raises(ValueError, match="No queries found"):
            run_benchmark(config, verbose=False)
