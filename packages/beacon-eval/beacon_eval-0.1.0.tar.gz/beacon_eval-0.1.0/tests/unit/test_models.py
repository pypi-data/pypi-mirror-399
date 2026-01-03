"""Tests for data models."""

import pytest
from pathlib import Path

from beacon.models import (
    BenchmarkConfig,
    BenchmarkResult,
    Chunk,
    ChunkingStrategy,
    ChunkingStrategyType,
    Document,
    Query,
    QueryResult,
    RetrievalMetrics,
    RetrievalResult,
    StrategyResult,
)


class TestChunkingStrategyType:
    """Tests for ChunkingStrategyType enum."""

    def test_enum_values(self) -> None:
        """Test all enum values exist."""
        assert ChunkingStrategyType.FIXED_SIZE.value == "fixed_size"
        assert ChunkingStrategyType.SENTENCE.value == "sentence"
        assert ChunkingStrategyType.PARAGRAPH.value == "paragraph"
        assert ChunkingStrategyType.SEMANTIC.value == "semantic"
        assert ChunkingStrategyType.RECURSIVE.value == "recursive"

    def test_enum_from_string(self) -> None:
        """Test creating enum from string."""
        assert ChunkingStrategyType("fixed_size") == ChunkingStrategyType.FIXED_SIZE
        assert ChunkingStrategyType("sentence") == ChunkingStrategyType.SENTENCE


class TestChunkingStrategy:
    """Tests for ChunkingStrategy dataclass."""

    def test_create_strategy(self) -> None:
        """Test creating a chunking strategy."""
        strategy = ChunkingStrategy(
            name="test",
            strategy_type=ChunkingStrategyType.FIXED_SIZE,
            chunk_size=256,
            chunk_overlap=25,
        )
        assert strategy.name == "test"
        assert strategy.strategy_type == ChunkingStrategyType.FIXED_SIZE
        assert strategy.chunk_size == 256
        assert strategy.chunk_overlap == 25
        assert strategy.params == {}

    def test_default_values(self) -> None:
        """Test default chunk size and overlap."""
        strategy = ChunkingStrategy(
            name="default",
            strategy_type=ChunkingStrategyType.SENTENCE,
        )
        assert strategy.chunk_size == 512
        assert strategy.chunk_overlap == 50

    def test_post_init_converts_string_type(self) -> None:
        """Test that string strategy_type is converted to enum."""
        strategy = ChunkingStrategy(
            name="test",
            strategy_type="fixed_size",  # type: ignore
        )
        assert strategy.strategy_type == ChunkingStrategyType.FIXED_SIZE

    def test_custom_params(self) -> None:
        """Test custom parameters."""
        strategy = ChunkingStrategy(
            name="custom",
            strategy_type=ChunkingStrategyType.SEMANTIC,
            params={"threshold": 0.5, "model": "custom-model"},
        )
        assert strategy.params["threshold"] == 0.5
        assert strategy.params["model"] == "custom-model"


class TestChunk:
    """Tests for Chunk dataclass."""

    def test_create_chunk(self) -> None:
        """Test creating a chunk."""
        chunk = Chunk(
            text="Hello world",
            doc_id="doc1",
            chunk_id="doc1_chunk_0",
            start_char=0,
            end_char=11,
            token_count=2,
        )
        assert chunk.text == "Hello world"
        assert chunk.doc_id == "doc1"
        assert chunk.chunk_id == "doc1_chunk_0"
        assert chunk.token_count == 2
        assert chunk.metadata == {}

    def test_chunk_with_metadata(self) -> None:
        """Test chunk with custom metadata."""
        chunk = Chunk(
            text="Test",
            doc_id="d1",
            chunk_id="c1",
            start_char=0,
            end_char=4,
            token_count=1,
            metadata={"strategy": "fixed", "source": "file.txt"},
        )
        assert chunk.metadata["strategy"] == "fixed"
        assert chunk.metadata["source"] == "file.txt"


class TestDocument:
    """Tests for Document dataclass."""

    def test_create_document(self) -> None:
        """Test creating a document."""
        doc = Document(doc_id="doc1", content="Test content")
        assert doc.doc_id == "doc1"
        assert doc.content == "Test content"
        assert doc.metadata == {}
        assert doc.source_path is None

    def test_document_with_path(self) -> None:
        """Test document with source path."""
        doc = Document(
            doc_id="doc1",
            content="Content",
            source_path=Path("/path/to/file.txt"),
        )
        assert doc.source_path == Path("/path/to/file.txt")


class TestQuery:
    """Tests for Query dataclass."""

    def test_create_query(self) -> None:
        """Test creating a query."""
        query = Query(
            query_id="q1",
            text="What is machine learning?",
            relevant_doc_ids=["doc1", "doc2"],
        )
        assert query.query_id == "q1"
        assert query.text == "What is machine learning?"
        assert query.relevant_doc_ids == ["doc1", "doc2"]
        assert query.relevant_chunk_ids == []

    def test_query_with_chunk_ids(self) -> None:
        """Test query with relevant chunk IDs."""
        query = Query(
            query_id="q1",
            text="Test",
            relevant_chunk_ids=["c1", "c2", "c3"],
        )
        assert query.relevant_chunk_ids == ["c1", "c2", "c3"]


class TestRetrievalResult:
    """Tests for RetrievalResult dataclass."""

    def test_create_result(self) -> None:
        """Test creating a retrieval result."""
        result = RetrievalResult(
            chunk_id="c1",
            doc_id="doc1",
            score=0.95,
            text="Retrieved text",
            rank=1,
        )
        assert result.chunk_id == "c1"
        assert result.score == 0.95
        assert result.rank == 1


class TestRetrievalMetrics:
    """Tests for RetrievalMetrics dataclass."""

    def test_default_metrics(self) -> None:
        """Test default metric values."""
        metrics = RetrievalMetrics()
        assert metrics.mrr == 0.0
        assert metrics.recall_at_1 == 0.0
        assert metrics.num_queries == 0

    def test_to_dict(self) -> None:
        """Test converting metrics to dictionary."""
        metrics = RetrievalMetrics(
            mrr=0.85,
            recall_at_1=0.7,
            recall_at_5=0.9,
            num_queries=100,
            num_chunks=500,
        )
        result = metrics.to_dict()
        assert result["mrr"] == 0.85
        assert result["recall@1"] == 0.7
        assert result["recall@5"] == 0.9
        assert result["num_queries"] == 100
        assert result["num_chunks"] == 500

    def test_to_dict_contains_all_fields(self) -> None:
        """Test that to_dict contains all expected fields."""
        metrics = RetrievalMetrics()
        result = metrics.to_dict()
        expected_keys = [
            "mrr",
            "recall@1",
            "recall@3",
            "recall@5",
            "recall@10",
            "precision@1",
            "precision@5",
            "ndcg@10",
            "map",
            "avg_latency_ms",
            "num_queries",
            "num_chunks",
            "avg_chunk_size",
        ]
        for key in expected_keys:
            assert key in result


class TestQueryResult:
    """Tests for QueryResult dataclass."""

    def test_create_query_result(self) -> None:
        """Test creating a query result."""
        result = QueryResult(
            query_id="q1",
            query_text="Test query",
            retrieved=[],
            relevant_doc_ids=["doc1"],
            relevant_chunk_ids=[],
            mrr=1.0,
            recall_at_1=1.0,
        )
        assert result.query_id == "q1"
        assert result.mrr == 1.0
        assert result.recall_at_1 == 1.0


class TestBenchmarkConfig:
    """Tests for BenchmarkConfig dataclass."""

    def test_create_config(self) -> None:
        """Test creating a benchmark config."""
        strategies = [
            ChunkingStrategy(
                name="test",
                strategy_type=ChunkingStrategyType.FIXED_SIZE,
            )
        ]
        config = BenchmarkConfig(
            name="test_benchmark",
            documents=[Path("doc1.txt")],
            queries_file=Path("queries.jsonl"),
            strategies=strategies,
        )
        assert config.name == "test_benchmark"
        assert config.embedding_model == "all-MiniLM-L6-v2"
        assert config.top_k == 10

    def test_default_values(self) -> None:
        """Test default config values."""
        config = BenchmarkConfig(
            name="test",
            documents=[],
            queries_file=Path("q.jsonl"),
            strategies=[],
        )
        assert config.cache_embeddings is True
        assert config.generate_html_report is True
        assert config.export_csv is True
        assert config.export_json is True


class TestBenchmarkResult:
    """Tests for BenchmarkResult dataclass."""

    @pytest.fixture
    def sample_result(self) -> BenchmarkResult:
        """Create a sample benchmark result."""
        strategy = ChunkingStrategy(
            name="fixed_512",
            strategy_type=ChunkingStrategyType.FIXED_SIZE,
            chunk_size=512,
            chunk_overlap=50,
        )
        metrics = RetrievalMetrics(mrr=0.85, recall_at_5=0.9)
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
        return BenchmarkResult(
            config=config,
            strategy_results=[strategy_result],
            best_strategy="fixed_512",
            recommendation="Use fixed_512",
        )

    def test_get_comparison_table(self, sample_result: BenchmarkResult) -> None:
        """Test generating comparison table."""
        table = sample_result.get_comparison_table()
        assert len(table) == 1
        assert table[0]["strategy"] == "fixed_512"
        assert table[0]["chunk_size"] == 512
        assert table[0]["mrr"] == 0.85
