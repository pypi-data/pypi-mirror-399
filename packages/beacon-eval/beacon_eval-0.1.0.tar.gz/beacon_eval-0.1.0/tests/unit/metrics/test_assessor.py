"""Tests for IR metrics assessment."""

import pytest

from beacon.metrics import MetricsEvaluator
from beacon.models import Query, RetrievalResult


@pytest.fixture
def assessor() -> MetricsEvaluator:
    """Create a metrics assessor."""
    return MetricsEvaluator(top_k=10)


class TestMetricsAssessor:
    """Tests for MetricsEvaluator."""

    def test_perfect_mrr(
        self,
        assessor: MetricsEvaluator,
        sample_query: Query,
        perfect_retrieval: list[RetrievalResult],
    ) -> None:
        """Test MRR is 1.0 when first result is relevant."""
        result = assessor.evaluate_query(sample_query, perfect_retrieval)
        assert result.mrr == 1.0

    def test_partial_mrr(
        self,
        assessor: MetricsEvaluator,
        sample_query: Query,
        partial_retrieval: list[RetrievalResult],
    ) -> None:
        """Test MRR is 0.5 when first relevant result is at rank 2."""
        result = assessor.evaluate_query(sample_query, partial_retrieval)
        assert result.mrr == 0.5

    def test_zero_mrr(
        self,
        assessor: MetricsEvaluator,
        sample_query: Query,
        no_relevant_retrieval: list[RetrievalResult],
    ) -> None:
        """Test MRR is 0 when no relevant results."""
        result = assessor.evaluate_query(sample_query, no_relevant_retrieval)
        assert result.mrr == 0.0

    def test_perfect_recall_at_1(
        self,
        assessor: MetricsEvaluator,
        sample_query: Query,
        perfect_retrieval: list[RetrievalResult],
    ) -> None:
        """Test Recall@1 when first result is relevant."""
        result = assessor.evaluate_query(sample_query, perfect_retrieval)
        assert result.recall_at_1 == 0.5  # 1 of 2 relevant docs

    def test_recall_at_5(
        self,
        assessor: MetricsEvaluator,
        sample_query: Query,
        perfect_retrieval: list[RetrievalResult],
    ) -> None:
        """Test Recall@5 with both relevant docs in top 5."""
        result = assessor.evaluate_query(sample_query, perfect_retrieval)
        assert result.recall_at_5 == 1.0  # Both relevant docs found

    def test_precision_at_1_perfect(
        self,
        assessor: MetricsEvaluator,
        sample_query: Query,
        perfect_retrieval: list[RetrievalResult],
    ) -> None:
        """Test Precision@1 when first result is relevant."""
        result = assessor.evaluate_query(sample_query, perfect_retrieval)
        assert result.precision_at_1 == 1.0

    def test_precision_at_1_zero(
        self,
        assessor: MetricsEvaluator,
        sample_query: Query,
        partial_retrieval: list[RetrievalResult],
    ) -> None:
        """Test Precision@1 when first result is not relevant."""
        result = assessor.evaluate_query(sample_query, partial_retrieval)
        assert result.precision_at_1 == 0.0

    def test_ndcg_at_10(
        self,
        assessor: MetricsEvaluator,
        sample_query: Query,
        perfect_retrieval: list[RetrievalResult],
    ) -> None:
        """Test NDCG@10 with perfect ordering."""
        result = assessor.evaluate_query(sample_query, perfect_retrieval)
        assert result.ndcg_at_10 == 1.0

    def test_aggregate_metrics(
        self,
        assessor: MetricsEvaluator,
        sample_query: Query,
        perfect_retrieval: list[RetrievalResult],
        partial_retrieval: list[RetrievalResult],
    ) -> None:
        """Test aggregation of metrics across queries."""
        result1 = assessor.evaluate_query(sample_query, perfect_retrieval)
        result2 = assessor.evaluate_query(sample_query, partial_retrieval)

        aggregated = assessor.aggregate_metrics([result1, result2])

        # Average of 1.0 and 0.5
        assert aggregated.mrr == 0.75
        assert aggregated.num_queries == 2

    def test_evaluate_with_chunk_ids(
        self,
        assessor: MetricsEvaluator,
    ) -> None:
        """Test evaluation when using chunk IDs instead of doc IDs."""
        query = Query(
            query_id="q1",
            text="test query",
            relevant_doc_ids=[],
            relevant_chunk_ids=["chunk_1", "chunk_2"],
        )
        retrieved = [
            RetrievalResult(chunk_id="chunk_1", doc_id="doc1", score=0.9, text="text1", rank=1),
            RetrievalResult(chunk_id="chunk_3", doc_id="doc2", score=0.8, text="text2", rank=2),
        ]
        result = assessor.evaluate_query(query, retrieved)
        assert result.mrr == 1.0
        assert result.recall_at_1 == 0.5

    def test_aggregate_empty_results(
        self,
        assessor: MetricsEvaluator,
    ) -> None:
        """Test aggregation with no results returns default metrics."""
        aggregated = assessor.aggregate_metrics([])
        assert aggregated.mrr == 0.0
        assert aggregated.num_queries == 0
