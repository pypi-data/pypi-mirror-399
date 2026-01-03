"""Shared pytest fixtures for beacon tests.

This file provides common fixtures used across multiple test modules.
pytest automatically discovers this file and makes fixtures available to all tests.
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock

import numpy as np

from beacon.models import (
    BenchmarkConfig,
    Chunk,
    ChunkingStrategy,
    ChunkingStrategyType,
    Document,
    Query,
    RetrievalMetrics,
    RetrievalResult,
    StrategyResult,
)


# =============================================================================
# Document Fixtures
# =============================================================================


@pytest.fixture
def sample_document() -> Document:
    """Create a sample document for testing."""
    return Document(
        doc_id="test_doc",
        content="""This is the first paragraph. It contains multiple sentences. Each sentence adds more content.

This is the second paragraph. It also has multiple sentences. The content continues here.

And this is the third paragraph. More text follows. This is important information.""",
    )


@pytest.fixture
def long_document() -> Document:
    """Create a longer document for testing."""
    sentences = [f"This is sentence number {i}. It contains some text." for i in range(100)]
    return Document(
        doc_id="long_doc",
        content=" ".join(sentences),
    )


@pytest.fixture
def sample_documents() -> list[Document]:
    """Create sample documents for testing."""
    return [
        Document(doc_id="doc1", content="Machine learning is a field of AI."),
        Document(doc_id="doc2", content="Deep learning uses neural networks."),
    ]


@pytest.fixture
def empty_document() -> Document:
    """Create an empty document."""
    return Document(doc_id="empty", content="")


# =============================================================================
# Query Fixtures
# =============================================================================


@pytest.fixture
def sample_query() -> Query:
    """Create a sample query with ground truth."""
    return Query(
        query_id="q1",
        text="Test query",
        relevant_doc_ids=["doc1", "doc2"],
    )


@pytest.fixture
def sample_queries() -> list[Query]:
    """Create sample queries for testing."""
    return [
        Query(query_id="q1", text="What is ML?", relevant_doc_ids=["doc1"]),
        Query(query_id="q2", text="Neural networks", relevant_doc_ids=["doc2"]),
    ]


# =============================================================================
# Retrieval Result Fixtures
# =============================================================================


@pytest.fixture
def perfect_retrieval() -> list[RetrievalResult]:
    """Create perfect retrieval results (relevant docs at top)."""
    return [
        RetrievalResult(chunk_id="c1", doc_id="doc1", score=0.9, text="", rank=1),
        RetrievalResult(chunk_id="c2", doc_id="doc2", score=0.8, text="", rank=2),
        RetrievalResult(chunk_id="c3", doc_id="doc3", score=0.7, text="", rank=3),
    ]


@pytest.fixture
def partial_retrieval() -> list[RetrievalResult]:
    """Create partial retrieval results (one relevant doc at rank 2)."""
    return [
        RetrievalResult(chunk_id="c1", doc_id="doc3", score=0.9, text="", rank=1),
        RetrievalResult(chunk_id="c2", doc_id="doc1", score=0.8, text="", rank=2),
        RetrievalResult(chunk_id="c3", doc_id="doc4", score=0.7, text="", rank=3),
    ]


@pytest.fixture
def no_relevant_retrieval() -> list[RetrievalResult]:
    """Create retrieval results with no relevant docs."""
    return [
        RetrievalResult(chunk_id="c1", doc_id="doc3", score=0.9, text="", rank=1),
        RetrievalResult(chunk_id="c2", doc_id="doc4", score=0.8, text="", rank=2),
    ]


# =============================================================================
# Chunking Strategy Fixtures
# =============================================================================


@pytest.fixture
def fixed_strategy() -> ChunkingStrategy:
    """Create a fixed-size chunking strategy."""
    return ChunkingStrategy(
        name="fixed_256",
        strategy_type=ChunkingStrategyType.FIXED_SIZE,
        chunk_size=256,
        chunk_overlap=25,
    )


@pytest.fixture
def sentence_strategy() -> ChunkingStrategy:
    """Create a sentence-based chunking strategy."""
    return ChunkingStrategy(
        name="sentence_512",
        strategy_type=ChunkingStrategyType.SENTENCE,
        chunk_size=512,
        chunk_overlap=50,
    )


# =============================================================================
# Chunk Fixtures
# =============================================================================


@pytest.fixture
def sample_chunks() -> list[Chunk]:
    """Create sample chunks for testing."""
    return [
        Chunk(
            text="Machine learning is a field of AI.",
            doc_id="doc1",
            chunk_id="doc1_chunk_0",
            start_char=0,
            end_char=34,
            token_count=8,
        ),
        Chunk(
            text="Deep learning uses neural networks.",
            doc_id="doc2",
            chunk_id="doc2_chunk_0",
            start_char=0,
            end_char=35,
            token_count=6,
        ),
    ]


# =============================================================================
# Embedding Mock Fixtures
# =============================================================================


@pytest.fixture
def mock_embeddings() -> np.ndarray:
    """Create mock embedding vectors."""
    return np.random.randn(2, 384).astype(np.float32)


@pytest.fixture
def mock_embedding_generator() -> MagicMock:
    """Create a mock embedding generator."""
    mock = MagicMock()
    mock.embed_queries.return_value = np.random.randn(2, 384).astype(np.float32)
    mock.embed_chunks.return_value = np.random.randn(2, 384).astype(np.float32)
    mock.embedding_dimension = 384
    return mock


# =============================================================================
# Config Fixtures
# =============================================================================


@pytest.fixture
def sample_config(tmp_path: Path) -> BenchmarkConfig:
    """Create a sample benchmark configuration."""
    strategy = ChunkingStrategy(
        name="test_strategy",
        strategy_type=ChunkingStrategyType.FIXED_SIZE,
        chunk_size=256,
        chunk_overlap=25,
    )
    queries_file = tmp_path / "queries.jsonl"
    queries_file.write_text('{"query_id": "q1", "text": "test", "relevant_doc_ids": ["doc1"]}')

    return BenchmarkConfig(
        name="test_benchmark",
        documents=[],
        queries_file=queries_file,
        strategies=[strategy],
    )


# =============================================================================
# Result Fixtures
# =============================================================================


@pytest.fixture
def sample_metrics() -> RetrievalMetrics:
    """Create sample retrieval metrics."""
    return RetrievalMetrics(
        mrr=0.85,
        recall_at_1=0.7,
        recall_at_5=0.9,
        num_queries=100,
        num_chunks=500,
    )


@pytest.fixture
def sample_strategy_result(
    fixed_strategy: ChunkingStrategy,
    sample_metrics: RetrievalMetrics,
    sample_chunks: list[Chunk],
) -> StrategyResult:
    """Create a sample strategy result."""
    return StrategyResult(
        strategy=fixed_strategy,
        metrics=sample_metrics,
        query_results=[],
        chunks=sample_chunks,
    )
