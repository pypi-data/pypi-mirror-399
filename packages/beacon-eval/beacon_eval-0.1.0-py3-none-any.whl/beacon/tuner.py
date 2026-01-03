"""Bayesian optimization for finding optimal chunking parameters."""

from typing import Any

from beacon.chunkers import get_chunker
from beacon.embeddings import EmbeddingGenerator
from beacon.indexers import FaissIndex
from beacon.metrics import MetricsEvaluator
from beacon.models import ChunkingStrategy, ChunkingStrategyType, Document, Query


class ChunkingTuner:
    """Auto-tune chunking parameters using Bayesian optimization."""

    def __init__(
        self,
        documents: list[Document],
        queries: list[Query],
        embedding_model: str = "all-MiniLM-L6-v2",
        metric: str = "mrr",
        n_trials: int = 50,
        top_k: int = 10,
    ) -> None:
        """Initialize the tuner.

        Args:
            documents: List of documents to chunk.
            queries: List of queries for evaluation.
            embedding_model: Name of embedding model.
            metric: Metric to optimize ('mrr', 'recall_at_5', 'ndcg_at_10').
            n_trials: Number of optimization trials.
            top_k: Number of results to retrieve.
        """
        self.documents = documents
        self.queries = queries
        self.embedding_model = embedding_model
        self.metric = metric
        self.n_trials = n_trials
        self.top_k = top_k

        self._embedding_generator = EmbeddingGenerator(model_name=embedding_model)
        self._evaluator = MetricsEvaluator(top_k=top_k)

        # Cache query embeddings
        self._query_embeddings = self._embedding_generator.embed_queries(
            queries, show_progress=False
        )

    def tune(
        self,
        strategy_type: ChunkingStrategyType = ChunkingStrategyType.FIXED_SIZE,
        chunk_size_range: tuple[int, int] = (100, 2000),
        overlap_range: tuple[int, int] = (0, 200),
        verbose: bool = True,
    ) -> dict[str, Any]:
        """Run Bayesian optimization to find optimal parameters.

        Args:
            strategy_type: Type of chunking strategy to optimize.
            chunk_size_range: Range of chunk sizes to search.
            overlap_range: Range of overlap sizes to search.
            verbose: Whether to show progress.

        Returns:
            Dictionary with optimal parameters and score.
        """
        try:
            import optuna
        except ImportError as err:
            raise ImportError(
                "optuna is required for auto-tuning. "
                "Install with: pip install optuna"
            ) from err

        # Suppress Optuna logging if not verbose
        if not verbose:
            optuna.logging.set_verbosity(optuna.logging.WARNING)

        def objective(trial: optuna.Trial) -> float:
            # Sample parameters
            chunk_size = trial.suggest_int(
                "chunk_size",
                chunk_size_range[0],
                chunk_size_range[1],
                step=50,
            )
            chunk_overlap = trial.suggest_int(
                "chunk_overlap",
                overlap_range[0],
                min(overlap_range[1], chunk_size // 2),
                step=10,
            )

            # Create strategy
            strategy = ChunkingStrategy(
                name=f"trial_{trial.number}",
                strategy_type=strategy_type,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            )

            # Evaluate
            score = self._evaluate_strategy(strategy)
            return score

        # Create study
        study = optuna.create_study(
            direction="maximize",
            sampler=optuna.samplers.TPESampler(seed=42),
        )

        # Run optimization
        study.optimize(
            objective,
            n_trials=self.n_trials,
            show_progress_bar=verbose,
        )

        # Get best parameters
        best_params = study.best_params
        best_score = study.best_value

        # Create optimal strategy
        optimal_strategy = ChunkingStrategy(
            name="optimal",
            strategy_type=strategy_type,
            chunk_size=best_params["chunk_size"],
            chunk_overlap=best_params["chunk_overlap"],
        )

        return {
            "optimal_strategy": optimal_strategy,
            "chunk_size": best_params["chunk_size"],
            "chunk_overlap": best_params["chunk_overlap"],
            f"best_{self.metric}": best_score,
            "n_trials": self.n_trials,
            "all_trials": [
                {
                    "params": t.params,
                    "score": t.value,
                }
                for t in study.trials
                if t.value is not None
            ],
        }

    def _evaluate_strategy(self, strategy: ChunkingStrategy) -> float:
        """Evaluate a chunking strategy and return the target metric.

        Args:
            strategy: The strategy to evaluate.

        Returns:
            The metric score.
        """
        # Get chunker and chunk documents
        chunker = get_chunker(strategy)
        chunks = chunker.chunk_documents(self.documents)

        if not chunks:
            return 0.0

        # Generate embeddings
        chunk_embeddings = self._embedding_generator.embed_chunks(
            chunks, show_progress=False, use_cache=False
        )

        # Build index
        index = FaissIndex(dimension=self._embedding_generator.embedding_dimension)
        index.add(chunks, chunk_embeddings)

        # Evaluate queries
        query_results = []
        for query, query_emb in zip(self.queries, self._query_embeddings, strict=True):
            retrieved, latency = index.search(query_emb, top_k=self.top_k)
            result = self._evaluator.evaluate_query(query, retrieved, latency)
            query_results.append(result)

        # Aggregate metrics
        metrics = self._evaluator.aggregate_metrics(query_results)

        # Return target metric
        if self.metric == "mrr":
            return metrics.mrr
        elif self.metric == "recall_at_5":
            return metrics.recall_at_5
        elif self.metric == "recall_at_10":
            return metrics.recall_at_10
        elif self.metric == "ndcg_at_10":
            return metrics.ndcg_at_10
        elif self.metric == "map":
            return metrics.map_score
        else:
            return metrics.mrr


def auto_tune(
    documents: list[Document],
    queries: list[Query],
    strategy_type: ChunkingStrategyType = ChunkingStrategyType.FIXED_SIZE,
    embedding_model: str = "all-MiniLM-L6-v2",
    metric: str = "mrr",
    n_trials: int = 50,
    chunk_size_range: tuple[int, int] = (100, 2000),
    overlap_range: tuple[int, int] = (0, 200),
    verbose: bool = True,
) -> dict[str, Any]:
    """Convenience function for auto-tuning chunking parameters.

    Args:
        documents: List of documents.
        queries: List of queries.
        strategy_type: Type of chunking strategy.
        embedding_model: Embedding model name.
        metric: Metric to optimize.
        n_trials: Number of optimization trials.
        chunk_size_range: Range for chunk size.
        overlap_range: Range for overlap.
        verbose: Whether to show progress.

    Returns:
        Dictionary with optimal parameters.
    """
    tuner = ChunkingTuner(
        documents=documents,
        queries=queries,
        embedding_model=embedding_model,
        metric=metric,
        n_trials=n_trials,
    )

    return tuner.tune(
        strategy_type=strategy_type,
        chunk_size_range=chunk_size_range,
        overlap_range=overlap_range,
        verbose=verbose,
    )
