"""IR metrics evaluation for retrieval quality."""

import math

from beacon.models import Query, QueryResult, RetrievalMetrics, RetrievalResult


class MetricsEvaluator:
    """Evaluator for Information Retrieval metrics."""

    def __init__(self, top_k: int = 10) -> None:
        """Initialize the evaluator.

        Args:
            top_k: Maximum k for Recall@K and other metrics.
        """
        self.top_k = top_k

    def evaluate_query(
        self,
        query: Query,
        retrieved: list[RetrievalResult],
        latency_ms: float = 0.0,
    ) -> QueryResult:
        """Evaluate retrieval results for a single query.

        Args:
            query: The query with ground truth.
            retrieved: List of retrieved results.
            latency_ms: Query latency in milliseconds.

        Returns:
            QueryResult with computed metrics.
        """
        # Get relevant IDs (either doc IDs or chunk IDs)
        relevant_ids = set(query.relevant_chunk_ids or query.relevant_doc_ids)

        # Get retrieved IDs - use doc_id if we're matching against doc IDs
        if query.relevant_chunk_ids:
            retrieved_ids = [r.chunk_id for r in retrieved]
        else:
            retrieved_ids = [r.doc_id for r in retrieved]

        # Calculate metrics
        mrr = self._calculate_mrr(retrieved_ids, relevant_ids)
        recall_at_1 = self._calculate_recall_at_k(retrieved_ids, relevant_ids, 1)
        recall_at_3 = self._calculate_recall_at_k(retrieved_ids, relevant_ids, 3)
        recall_at_5 = self._calculate_recall_at_k(retrieved_ids, relevant_ids, 5)
        recall_at_10 = self._calculate_recall_at_k(retrieved_ids, relevant_ids, 10)
        precision_at_1 = self._calculate_precision_at_k(retrieved_ids, relevant_ids, 1)
        precision_at_5 = self._calculate_precision_at_k(retrieved_ids, relevant_ids, 5)
        ndcg_at_10 = self._calculate_ndcg_at_k(retrieved_ids, relevant_ids, 10)

        return QueryResult(
            query_id=query.query_id,
            query_text=query.text,
            retrieved=retrieved,
            relevant_doc_ids=query.relevant_doc_ids,
            relevant_chunk_ids=query.relevant_chunk_ids,
            mrr=mrr,
            recall_at_1=recall_at_1,
            recall_at_3=recall_at_3,
            recall_at_5=recall_at_5,
            recall_at_10=recall_at_10,
            precision_at_1=precision_at_1,
            precision_at_5=precision_at_5,
            ndcg_at_10=ndcg_at_10,
            latency_ms=latency_ms,
        )

    def aggregate_metrics(
        self,
        query_results: list[QueryResult],
        num_chunks: int = 0,
        avg_chunk_size: float = 0.0,
    ) -> RetrievalMetrics:
        """Aggregate metrics across all queries.

        Args:
            query_results: List of QueryResult objects.
            num_chunks: Total number of chunks.
            avg_chunk_size: Average chunk size in tokens.

        Returns:
            Aggregated RetrievalMetrics.
        """
        if not query_results:
            return RetrievalMetrics()

        n = len(query_results)

        return RetrievalMetrics(
            mrr=sum(qr.mrr for qr in query_results) / n,
            recall_at_1=sum(qr.recall_at_1 for qr in query_results) / n,
            recall_at_3=sum(qr.recall_at_3 for qr in query_results) / n,
            recall_at_5=sum(qr.recall_at_5 for qr in query_results) / n,
            recall_at_10=sum(qr.recall_at_10 for qr in query_results) / n,
            precision_at_1=sum(qr.precision_at_1 for qr in query_results) / n,
            precision_at_5=sum(qr.precision_at_5 for qr in query_results) / n,
            ndcg_at_10=sum(qr.ndcg_at_10 for qr in query_results) / n,
            map_score=self._calculate_map(query_results),
            avg_latency_ms=sum(qr.latency_ms for qr in query_results) / n,
            num_queries=n,
            num_chunks=num_chunks,
            avg_chunk_size=avg_chunk_size,
        )

    def _calculate_mrr(
        self,
        retrieved_ids: list[str],
        relevant_ids: set[str],
    ) -> float:
        """Calculate Mean Reciprocal Rank.

        Args:
            retrieved_ids: List of retrieved IDs in order.
            relevant_ids: Set of relevant IDs.

        Returns:
            MRR score (1/rank of first relevant result, or 0).
        """
        for rank, rid in enumerate(retrieved_ids, 1):
            if rid in relevant_ids:
                return 1.0 / rank
        return 0.0

    def _calculate_recall_at_k(
        self,
        retrieved_ids: list[str],
        relevant_ids: set[str],
        k: int,
    ) -> float:
        """Calculate Recall@K.

        Args:
            retrieved_ids: List of retrieved IDs.
            relevant_ids: Set of relevant IDs.
            k: Number of top results to consider.

        Returns:
            Recall@K score.
        """
        if not relevant_ids:
            return 0.0

        retrieved_at_k = set(retrieved_ids[:k])
        hits = len(retrieved_at_k & relevant_ids)
        return hits / len(relevant_ids)

    def _calculate_precision_at_k(
        self,
        retrieved_ids: list[str],
        relevant_ids: set[str],
        k: int,
    ) -> float:
        """Calculate Precision@K.

        Args:
            retrieved_ids: List of retrieved IDs.
            relevant_ids: Set of relevant IDs.
            k: Number of top results to consider.

        Returns:
            Precision@K score.
        """
        retrieved_at_k = list(retrieved_ids[:k])
        if not retrieved_at_k:
            return 0.0

        hits = sum(1 for rid in retrieved_at_k if rid in relevant_ids)
        return hits / len(retrieved_at_k)

    def _calculate_ndcg_at_k(
        self,
        retrieved_ids: list[str],
        relevant_ids: set[str],
        k: int,
    ) -> float:
        """Calculate Normalized Discounted Cumulative Gain at K.

        Args:
            retrieved_ids: List of retrieved IDs.
            relevant_ids: Set of relevant IDs.
            k: Number of top results to consider.

        Returns:
            NDCG@K score.
        """
        # Calculate DCG
        dcg = 0.0
        for i, rid in enumerate(retrieved_ids[:k]):
            if rid in relevant_ids:
                # Binary relevance (1 if relevant, 0 otherwise)
                dcg += 1.0 / math.log2(i + 2)  # +2 because log2(1) = 0

        # Calculate ideal DCG
        num_relevant = min(len(relevant_ids), k)
        idcg = sum(1.0 / math.log2(i + 2) for i in range(num_relevant))

        if idcg == 0:
            return 0.0

        return dcg / idcg

    def _calculate_map(self, query_results: list[QueryResult]) -> float:
        """Calculate Mean Average Precision across all queries.

        Args:
            query_results: List of QueryResult objects.

        Returns:
            MAP score.
        """
        if not query_results:
            return 0.0

        ap_scores = []
        for qr in query_results:
            relevant_ids = set(qr.relevant_chunk_ids or qr.relevant_doc_ids)
            if not relevant_ids:
                continue

            if qr.relevant_chunk_ids:
                retrieved_ids = [r.chunk_id for r in qr.retrieved]
            else:
                retrieved_ids = [r.doc_id for r in qr.retrieved]

            ap = self._calculate_average_precision(retrieved_ids, relevant_ids)
            ap_scores.append(ap)

        return sum(ap_scores) / len(ap_scores) if ap_scores else 0.0

    def _calculate_average_precision(
        self,
        retrieved_ids: list[str],
        relevant_ids: set[str],
    ) -> float:
        """Calculate Average Precision for a single query.

        Args:
            retrieved_ids: List of retrieved IDs.
            relevant_ids: Set of relevant IDs.

        Returns:
            AP score.
        """
        if not relevant_ids:
            return 0.0

        hits = 0
        sum_precisions = 0.0

        for i, rid in enumerate(retrieved_ids):
            if rid in relevant_ids:
                hits += 1
                precision_at_i = hits / (i + 1)
                sum_precisions += precision_at_i

        return sum_precisions / len(relevant_ids)
