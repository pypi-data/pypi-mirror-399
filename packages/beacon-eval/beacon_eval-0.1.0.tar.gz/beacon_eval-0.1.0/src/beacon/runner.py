"""Benchmark runner for evaluating chunking strategies."""

import json
import time
from pathlib import Path
from typing import Any

from rich.console import Console

from beacon.chunkers import get_chunker
from beacon.embeddings import EmbeddingGenerator
from beacon.indexers import FaissIndex
from beacon.metrics import MetricsEvaluator
from beacon.models import (
    BenchmarkConfig,
    BenchmarkResult,
    ChunkingStrategy,
    Document,
    Query,
    StrategyResult,
)
from beacon.parsers import load_documents, load_queries

console = Console()


def run_benchmark(
    config: BenchmarkConfig,
    verbose: bool = True,
) -> BenchmarkResult:
    """Run a complete benchmark evaluation.

    Args:
        config: Benchmark configuration.
        verbose: Whether to show progress.

    Returns:
        BenchmarkResult with all strategy evaluations.
    """
    start_time = time.time()

    # Load documents
    if verbose:
        console.print("[dim]Loading documents...[/dim]")
    documents = load_documents(config.documents)

    if not documents:
        raise ValueError("No documents found to evaluate")

    if verbose:
        console.print(f"[dim]Loaded {len(documents)} documents[/dim]")

    # Load queries
    if verbose:
        console.print("[dim]Loading queries...[/dim]")
    queries = load_queries(config.queries_file)

    if not queries:
        raise ValueError("No queries found to evaluate")

    if verbose:
        console.print(f"[dim]Loaded {len(queries)} queries[/dim]")

    # Initialize embedding generator
    cache_dir = config.output_dir / ".cache" if config.cache_embeddings else None
    embedding_generator = EmbeddingGenerator(
        model_name=config.embedding_model,
        cache_dir=cache_dir,
    )

    # Initialize metrics evaluator
    evaluator = MetricsEvaluator(top_k=config.top_k)

    # Evaluate each strategy
    strategy_results: list[StrategyResult] = []

    for strategy in config.strategies:
        if verbose:
            console.print(f"\n[bold]Evaluating strategy:[/bold] {strategy.name}")

        strategy_result = evaluate_strategy(
            strategy=strategy,
            documents=documents,
            queries=queries,
            embedding_generator=embedding_generator,
            evaluator=evaluator,
            top_k=config.top_k,
            verbose=verbose,
        )
        strategy_results.append(strategy_result)

    # Determine best strategy
    best_strategy = max(strategy_results, key=lambda r: r.metrics.mrr)
    recommendation = _generate_recommendation(strategy_results, best_strategy)

    total_time_ms = (time.time() - start_time) * 1000

    result = BenchmarkResult(
        config=config,
        strategy_results=strategy_results,
        best_strategy=best_strategy.strategy.name,
        recommendation=recommendation,
        total_time_ms=total_time_ms,
    )

    # Export results
    _export_results(result, config)

    return result


def evaluate_strategy(
    strategy: ChunkingStrategy,
    documents: list[Document],
    queries: list[Query],
    embedding_generator: EmbeddingGenerator,
    evaluator: MetricsEvaluator,
    top_k: int = 10,
    verbose: bool = True,
) -> StrategyResult:
    """Evaluate a single chunking strategy.

    Args:
        strategy: The chunking strategy to evaluate.
        documents: List of documents.
        queries: List of queries.
        embedding_generator: Embedding generator.
        evaluator: Metrics evaluator.
        top_k: Number of results to retrieve.
        verbose: Whether to show progress.

    Returns:
        StrategyResult with metrics.
    """
    # Get chunker
    chunker = get_chunker(strategy)

    # Chunk documents
    if verbose:
        console.print("  [dim]Chunking documents...[/dim]")

    chunks = chunker.chunk_documents(documents)

    if verbose:
        console.print(f"  [dim]Created {len(chunks)} chunks[/dim]")

    # Generate embeddings
    if verbose:
        console.print("  [dim]Generating embeddings...[/dim]")

    embed_start = time.time()
    chunk_embeddings = embedding_generator.embed_chunks(chunks, show_progress=verbose)
    embedding_time_ms = (time.time() - embed_start) * 1000

    # Build index
    if verbose:
        console.print("  [dim]Building index...[/dim]")

    index_start = time.time()
    index = FaissIndex(dimension=embedding_generator.embedding_dimension)
    index.add(chunks, chunk_embeddings)
    indexing_time_ms = (time.time() - index_start) * 1000

    # Evaluate queries
    if verbose:
        console.print(f"  [dim]Evaluating {len(queries)} queries...[/dim]")

    query_embeddings = embedding_generator.embed_queries(queries, show_progress=False)

    query_results = []
    for query, query_emb in zip(queries, query_embeddings, strict=True):
        retrieved, latency = index.search(query_emb, top_k=top_k)
        result = evaluator.evaluate_query(query, retrieved, latency)
        query_results.append(result)

    # Aggregate metrics
    avg_chunk_size = sum(c.token_count for c in chunks) / len(chunks) if chunks else 0
    metrics = evaluator.aggregate_metrics(
        query_results,
        num_chunks=len(chunks),
        avg_chunk_size=avg_chunk_size,
    )

    return StrategyResult(
        strategy=strategy,
        metrics=metrics,
        query_results=query_results,
        chunks=chunks,
        embedding_time_ms=embedding_time_ms,
        indexing_time_ms=indexing_time_ms,
    )


def _generate_recommendation(
    results: list[StrategyResult],
    best: StrategyResult,
) -> str:
    """Generate a recommendation based on results.

    Args:
        results: All strategy results.
        best: The best performing strategy.

    Returns:
        Recommendation string.
    """
    # Analyze results
    mrr_scores = {r.strategy.name: r.metrics.mrr for r in results}
    best_mrr = best.metrics.mrr

    # Check if there's a clear winner
    second_best = sorted(mrr_scores.values(), reverse=True)[1] if len(mrr_scores) > 1 else 0
    margin = best_mrr - second_best

    if margin > 0.1:
        confidence = "strongly"
    elif margin > 0.05:
        confidence = "moderately"
    else:
        confidence = "slightly"

    recommendation = (
        f"Based on MRR scores, {best.strategy.name} is {confidence} recommended "
        f"with MRR={best_mrr:.3f}. "
    )

    # Add chunk size insight
    if best.strategy.chunk_size < 400:
        recommendation += "Smaller chunk sizes work better for your queries. "
    elif best.strategy.chunk_size > 800:
        recommendation += "Larger chunk sizes preserve more context for your queries. "

    return recommendation


def _export_results(result: BenchmarkResult, config: BenchmarkConfig) -> None:
    """Export benchmark results to files.

    Args:
        result: Benchmark result.
        config: Benchmark configuration.
    """
    output_dir = config.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    # Export JSON
    if config.export_json:
        json_path = output_dir / "results.json"
        with open(json_path, "w") as f:
            json.dump(_result_to_dict(result), f, indent=2, default=str)

    # Export CSV
    if config.export_csv:
        _export_csv(result, output_dir / "results.csv")

    # Generate HTML report
    if config.generate_html_report:
        from beacon.reporters import generate_html_report

        generate_html_report(result, output_dir / "report.html")


def _result_to_dict(result: BenchmarkResult) -> dict[str, Any]:
    """Convert BenchmarkResult to dictionary for JSON export."""
    return {
        "config": {
            "name": result.config.name,
            "embedding_model": result.config.embedding_model,
            "top_k": result.config.top_k,
            "num_documents": len(result.config.documents),
        },
        "best_strategy": result.best_strategy,
        "recommendation": result.recommendation,
        "total_time_ms": result.total_time_ms,
        "strategy_results": [
            {
                "strategy": {
                    "name": sr.strategy.name,
                    "type": sr.strategy.strategy_type.value,
                    "chunk_size": sr.strategy.chunk_size,
                    "overlap": sr.strategy.chunk_overlap,
                },
                "metrics": sr.metrics.to_dict(),
                "embedding_time_ms": sr.embedding_time_ms,
                "indexing_time_ms": sr.indexing_time_ms,
            }
            for sr in result.strategy_results
        ],
    }


def _export_csv(result: BenchmarkResult, path: Path) -> None:
    """Export results as CSV."""
    import csv

    with open(path, "w", newline="") as f:
        writer = csv.writer(f)

        # Header
        writer.writerow(
            [
                "Strategy",
                "Type",
                "Chunk Size",
                "Overlap",
                "Num Chunks",
                "MRR",
                "Recall@1",
                "Recall@5",
                "Recall@10",
                "NDCG@10",
                "Avg Latency (ms)",
            ]
        )

        # Data
        for sr in result.strategy_results:
            writer.writerow(
                [
                    sr.strategy.name,
                    sr.strategy.strategy_type.value,
                    sr.strategy.chunk_size,
                    sr.strategy.chunk_overlap,
                    sr.metrics.num_chunks,
                    f"{sr.metrics.mrr:.4f}",
                    f"{sr.metrics.recall_at_1:.4f}",
                    f"{sr.metrics.recall_at_5:.4f}",
                    f"{sr.metrics.recall_at_10:.4f}",
                    f"{sr.metrics.ndcg_at_10:.4f}",
                    f"{sr.metrics.avg_latency_ms:.2f}",
                ]
            )
