"""Integration tests for the full benchmark workflow.

These tests verify that all components work together correctly,
from document loading through chunking, embedding, indexing, and evaluation.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np

from beacon.chunkers import get_chunker
from beacon.config import load_config
from beacon.embeddings import EmbeddingGenerator
from beacon.indexers import FaissIndex
from beacon.metrics import MetricsEvaluator
from beacon.models import (
    BenchmarkConfig,
    ChunkingStrategy,
    ChunkingStrategyType,
    Document,
    Query,
)
from beacon.parsers import load_documents, load_queries


@pytest.fixture
def integration_docs_dir(tmp_path: Path) -> Path:
    """Create a directory with sample documents."""
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()

    (docs_dir / "ml_intro.txt").write_text(
        "Machine learning is a subset of artificial intelligence. "
        "It enables computers to learn from data without being explicitly programmed. "
        "Supervised learning uses labeled data to train models. "
        "Unsupervised learning finds patterns in unlabeled data."
    )

    (docs_dir / "deep_learning.txt").write_text(
        "Deep learning uses neural networks with multiple layers. "
        "Convolutional neural networks are used for image processing. "
        "Recurrent neural networks handle sequential data. "
        "Transformers have revolutionized natural language processing."
    )

    (docs_dir / "nlp_basics.txt").write_text(
        "Natural language processing enables computers to understand text. "
        "Tokenization breaks text into smaller units called tokens. "
        "Word embeddings represent words as dense vectors. "
        "Named entity recognition identifies entities in text."
    )

    return docs_dir


@pytest.fixture
def integration_queries_file(tmp_path: Path) -> Path:
    """Create a queries file with ground truth."""
    queries_file = tmp_path / "queries.jsonl"
    queries = [
        {
            "query_id": "q1",
            "query": "What is machine learning?",
            "relevant_doc_ids": ["ml_intro"],
        },
        {
            "query_id": "q2",
            "query": "How do neural networks work?",
            "relevant_doc_ids": ["deep_learning"],
        },
        {
            "query_id": "q3",
            "query": "What is tokenization in NLP?",
            "relevant_doc_ids": ["nlp_basics"],
        },
    ]
    with open(queries_file, "w") as f:
        for q in queries:
            f.write(json.dumps(q) + "\n")
    return queries_file


@pytest.fixture
def integration_config_file(
    tmp_path: Path,
    integration_docs_dir: Path,
    integration_queries_file: Path,
) -> Path:
    """Create a complete benchmark config file."""
    config = {
        "name": "integration_test_benchmark",
        "documents": [str(integration_docs_dir)],
        "queries": str(integration_queries_file),
        "embedding_model": "all-MiniLM-L6-v2",
        "top_k": 5,
        "strategies": [
            {
                "name": "fixed_128",
                "type": "fixed_size",
                "chunk_size": 128,
                "chunk_overlap": 20,
            },
            {
                "name": "sentence_256",
                "type": "sentence",
                "chunk_size": 256,
                "chunk_overlap": 25,
            },
        ],
    }
    config_file = tmp_path / "beacon.yaml"
    import yaml
    with open(config_file, "w") as f:
        yaml.dump(config, f)
    return config_file


class TestDocumentToChunkFlow:
    """Tests for document loading and chunking integration."""

    def test_load_and_chunk_documents(self, integration_docs_dir: Path) -> None:
        """Test loading documents and chunking them."""
        # Load documents
        documents = load_documents([integration_docs_dir])
        assert len(documents) == 3

        # Chunk with fixed-size strategy
        strategy = ChunkingStrategy(
            name="fixed_100",
            strategy_type=ChunkingStrategyType.FIXED_SIZE,
            chunk_size=100,
            chunk_overlap=10,
        )
        chunker = get_chunker(strategy)
        chunks = chunker.chunk_documents(documents)

        assert len(chunks) > 0
        # Each document should produce at least one chunk
        doc_ids = {c.doc_id for c in chunks}
        assert len(doc_ids) == 3

    def test_multiple_chunking_strategies(self, integration_docs_dir: Path) -> None:
        """Test that different strategies produce different chunks."""
        documents = load_documents([integration_docs_dir])

        strategies = [
            ChunkingStrategy(
                name="fixed_25",
                strategy_type=ChunkingStrategyType.FIXED_SIZE,
                chunk_size=25,
                chunk_overlap=0,
            ),
            ChunkingStrategy(
                name="fixed_500",
                strategy_type=ChunkingStrategyType.FIXED_SIZE,
                chunk_size=500,
                chunk_overlap=0,
            ),
            ChunkingStrategy(
                name="sentence",
                strategy_type=ChunkingStrategyType.SENTENCE,
                chunk_size=150,
                chunk_overlap=0,
            ),
        ]

        chunk_counts = []
        for strategy in strategies:
            chunker = get_chunker(strategy)
            chunks = chunker.chunk_documents(documents)
            chunk_counts.append(len(chunks))

        # Different strategies should produce different numbers of chunks
        # Smaller chunk size should produce more chunks
        assert chunk_counts[0] >= chunk_counts[1]
        # All strategies should produce at least one chunk
        assert all(count > 0 for count in chunk_counts)


class TestChunkToIndexFlow:
    """Tests for chunking to indexing integration."""

    def test_chunk_embed_and_index(self, integration_docs_dir: Path) -> None:
        """Test chunking, embedding, and indexing documents."""
        documents = load_documents([integration_docs_dir])

        # Chunk
        strategy = ChunkingStrategy(
            name="fixed",
            strategy_type=ChunkingStrategyType.FIXED_SIZE,
            chunk_size=150,
            chunk_overlap=20,
        )
        chunker = get_chunker(strategy)
        chunks = chunker.chunk_documents(documents)

        # Create mock embeddings
        embedding_dim = 384
        mock_embeddings = np.random.randn(len(chunks), embedding_dim).astype(np.float32)

        # Index
        index = FaissIndex(dimension=embedding_dim)
        index.add(chunks, mock_embeddings)

        assert index.num_chunks == len(chunks)

        # Search should return results
        query_embedding = np.random.randn(embedding_dim).astype(np.float32)
        results, latency = index.search(query_embedding, top_k=3)

        assert len(results) == 3
        assert latency >= 0


class TestEndToEndRetrieval:
    """Tests for end-to-end retrieval with mocked embeddings."""

    def test_full_retrieval_pipeline(
        self,
        integration_docs_dir: Path,
        integration_queries_file: Path,
    ) -> None:
        """Test the full retrieval pipeline with mocked embeddings."""
        # Load documents and queries
        documents = load_documents([integration_docs_dir])
        queries = load_queries(integration_queries_file)

        assert len(documents) == 3
        assert len(queries) == 3

        # Chunk documents
        strategy = ChunkingStrategy(
            name="fixed",
            strategy_type=ChunkingStrategyType.FIXED_SIZE,
            chunk_size=200,
            chunk_overlap=25,
        )
        chunker = get_chunker(strategy)
        chunks = chunker.chunk_documents(documents)

        # Create embeddings that will produce good retrieval results
        # Make chunk embeddings similar to their source document queries
        embedding_dim = 128
        chunk_embeddings = []
        for chunk in chunks:
            if "ml_intro" in chunk.doc_id:
                # Similar to query about ML
                base = np.array([1.0, 0.0, 0.0, 0.0])
            elif "deep_learning" in chunk.doc_id:
                # Similar to query about neural networks
                base = np.array([0.0, 1.0, 0.0, 0.0])
            else:
                # Similar to query about NLP
                base = np.array([0.0, 0.0, 1.0, 0.0])
            # Extend to full dimension with noise
            embedding = np.concatenate([base, np.random.randn(embedding_dim - 4) * 0.1])
            chunk_embeddings.append(embedding)
        chunk_embeddings = np.array(chunk_embeddings, dtype=np.float32)

        # Create query embeddings
        query_embeddings = np.array([
            np.concatenate([[1.0, 0.0, 0.0, 0.0], np.zeros(embedding_dim - 4)]),  # ML query
            np.concatenate([[0.0, 1.0, 0.0, 0.0], np.zeros(embedding_dim - 4)]),  # NN query
            np.concatenate([[0.0, 0.0, 1.0, 0.0], np.zeros(embedding_dim - 4)]),  # NLP query
        ], dtype=np.float32)

        # Build index
        index = FaissIndex(dimension=embedding_dim)
        index.add(chunks, chunk_embeddings)

        # Search and assess
        assessor = MetricsEvaluator(top_k=5)
        query_results = []

        for i, query in enumerate(queries):
            results, _ = index.search(query_embeddings[i], top_k=5)
            query_result = assessor.evaluate_query(query, results)
            query_results.append(query_result)

        # Aggregate metrics
        metrics = assessor.aggregate_metrics(query_results)

        # With our engineered embeddings, we should get good retrieval
        assert metrics.mrr > 0.5
        assert metrics.num_queries == 3


class TestConfigToRunFlow:
    """Tests for config loading to benchmark execution."""

    def test_load_config_and_parse(self, integration_config_file: Path) -> None:
        """Test loading and parsing a config file."""
        # load_config already returns a parsed BenchmarkConfig
        config = load_config(integration_config_file)

        assert config.name == "integration_test_benchmark"
        assert len(config.strategies) == 2
        assert config.top_k == 5

    def test_config_strategies_are_valid(self, integration_config_file: Path) -> None:
        """Test that config strategies can be used to create chunkers."""
        config = load_config(integration_config_file)

        for strategy in config.strategies:
            chunker = get_chunker(strategy)
            assert chunker is not None
            assert chunker.strategy == strategy


class TestMultiStrategyComparison:
    """Tests for comparing multiple chunking strategies."""

    def test_compare_strategy_metrics(
        self,
        integration_docs_dir: Path,
        integration_queries_file: Path,
    ) -> None:
        """Test comparing metrics across strategies."""
        documents = load_documents([integration_docs_dir])
        queries = load_queries(integration_queries_file)

        strategies = [
            ChunkingStrategy(
                name="small_chunks",
                strategy_type=ChunkingStrategyType.FIXED_SIZE,
                chunk_size=25,
                chunk_overlap=5,
            ),
            ChunkingStrategy(
                name="large_chunks",
                strategy_type=ChunkingStrategyType.FIXED_SIZE,
                chunk_size=500,
                chunk_overlap=50,
            ),
        ]

        embedding_dim = 64
        results = {}

        for strategy in strategies:
            # Chunk
            chunker = get_chunker(strategy)
            chunks = chunker.chunk_documents(documents)

            # Create random embeddings (not meaningful, just for testing flow)
            chunk_embeddings = np.random.randn(len(chunks), embedding_dim).astype(np.float32)
            query_embeddings = np.random.randn(len(queries), embedding_dim).astype(np.float32)

            # Index and search
            index = FaissIndex(dimension=embedding_dim)
            index.add(chunks, chunk_embeddings)

            assessor = MetricsEvaluator(top_k=5)
            query_results = []

            for i, query in enumerate(queries):
                search_results, _ = index.search(query_embeddings[i], top_k=5)
                qr = assessor.evaluate_query(query, search_results)
                query_results.append(qr)

            metrics = assessor.aggregate_metrics(query_results)
            results[strategy.name] = {
                "num_chunks": len(chunks),
                "mrr": metrics.mrr,
                "recall_at_5": metrics.recall_at_5,
            }

        # Verify we have results for both strategies
        assert "small_chunks" in results
        assert "large_chunks" in results
        # Small chunks should produce more chunks
        assert results["small_chunks"]["num_chunks"] > results["large_chunks"]["num_chunks"]
