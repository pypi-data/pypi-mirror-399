"""Core data models for Beacon."""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class ChunkingStrategyType(Enum):
    """Supported chunking strategy types."""

    FIXED_SIZE = "fixed_size"
    SENTENCE = "sentence"
    PARAGRAPH = "paragraph"
    SEMANTIC = "semantic"
    RECURSIVE = "recursive"


@dataclass
class ChunkingStrategy:
    """Configuration for a chunking strategy."""

    name: str
    strategy_type: ChunkingStrategyType
    chunk_size: int = 512
    chunk_overlap: int = 50
    # Additional strategy-specific parameters
    params: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if isinstance(self.strategy_type, str):
            self.strategy_type = ChunkingStrategyType(self.strategy_type)


@dataclass
class Chunk:
    """A single chunk of text with metadata."""

    text: str
    doc_id: str
    chunk_id: str
    start_char: int
    end_char: int
    token_count: int
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Document:
    """A document to be chunked."""

    doc_id: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    source_path: Path | None = None


@dataclass
class Query:
    """A benchmark query with expected results."""

    query_id: str
    text: str
    relevant_doc_ids: list[str] = field(default_factory=list)
    relevant_chunk_ids: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RetrievalResult:
    """Result of retrieving chunks for a query."""

    chunk_id: str
    doc_id: str
    score: float
    text: str
    rank: int


@dataclass
class QueryResult:
    """Evaluation result for a single query."""

    query_id: str
    query_text: str
    retrieved: list[RetrievalResult]
    relevant_doc_ids: list[str]
    relevant_chunk_ids: list[str]
    # Metrics for this query
    mrr: float = 0.0
    recall_at_1: float = 0.0
    recall_at_3: float = 0.0
    recall_at_5: float = 0.0
    recall_at_10: float = 0.0
    precision_at_1: float = 0.0
    precision_at_5: float = 0.0
    ndcg_at_10: float = 0.0
    latency_ms: float = 0.0


@dataclass
class RetrievalMetrics:
    """Aggregated retrieval metrics across all queries."""

    mrr: float = 0.0
    recall_at_1: float = 0.0
    recall_at_3: float = 0.0
    recall_at_5: float = 0.0
    recall_at_10: float = 0.0
    precision_at_1: float = 0.0
    precision_at_5: float = 0.0
    ndcg_at_10: float = 0.0
    map_score: float = 0.0
    avg_latency_ms: float = 0.0
    # Additional statistics
    num_queries: int = 0
    num_chunks: int = 0
    avg_chunk_size: float = 0.0

    def to_dict(self) -> dict[str, float | int]:
        """Convert metrics to dictionary."""
        return {
            "mrr": self.mrr,
            "recall@1": self.recall_at_1,
            "recall@3": self.recall_at_3,
            "recall@5": self.recall_at_5,
            "recall@10": self.recall_at_10,
            "precision@1": self.precision_at_1,
            "precision@5": self.precision_at_5,
            "ndcg@10": self.ndcg_at_10,
            "map": self.map_score,
            "avg_latency_ms": self.avg_latency_ms,
            "num_queries": self.num_queries,
            "num_chunks": self.num_chunks,
            "avg_chunk_size": self.avg_chunk_size,
        }


@dataclass
class StrategyResult:
    """Benchmark result for a single strategy."""

    strategy: ChunkingStrategy
    metrics: RetrievalMetrics
    query_results: list[QueryResult]
    chunks: list[Chunk]
    embedding_time_ms: float = 0.0
    indexing_time_ms: float = 0.0


@dataclass
class BenchmarkConfig:
    """Configuration for a benchmark run."""

    name: str
    documents: list[Path]
    queries_file: Path
    strategies: list[ChunkingStrategy]
    embedding_model: str = "all-MiniLM-L6-v2"
    top_k: int = 10
    output_dir: Path = field(default_factory=lambda: Path("./beacon_results"))
    # Optional settings
    cache_embeddings: bool = True
    generate_html_report: bool = True
    export_csv: bool = True
    export_json: bool = True


@dataclass
class BenchmarkResult:
    """Complete benchmark result across all strategies."""

    config: BenchmarkConfig
    strategy_results: list[StrategyResult]
    best_strategy: str
    recommendation: str
    total_time_ms: float = 0.0

    def get_comparison_table(self) -> list[dict[str, Any]]:
        """Get comparison table of all strategies."""
        rows = []
        for sr in self.strategy_results:
            row = {
                "strategy": sr.strategy.name,
                "chunk_size": sr.strategy.chunk_size,
                "overlap": sr.strategy.chunk_overlap,
                **sr.metrics.to_dict(),
            }
            rows.append(row)
        return rows
