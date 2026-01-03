"""Beacon - RAG Chunking Strategy Benchmarking Toolkit.

A benchmarking toolkit that evaluates and compares RAG chunking strategies
against your actual queries to find the optimal configuration.
"""

__version__ = "0.1.0"

from beacon.models import (
    BenchmarkConfig,
    BenchmarkResult,
    ChunkingStrategy,
    QueryResult,
    RetrievalMetrics,
)

__all__ = [
    "__version__",
    "BenchmarkConfig",
    "BenchmarkResult",
    "ChunkingStrategy",
    "QueryResult",
    "RetrievalMetrics",
]
