"""Tests for report generation."""

import pytest
from pathlib import Path

from beacon.models import (
    BenchmarkConfig,
    BenchmarkResult,
    ChunkingStrategy,
    ChunkingStrategyType,
    RetrievalMetrics,
    StrategyResult,
)
from beacon.reporters import generate_html_report


@pytest.fixture
def report_result() -> BenchmarkResult:
    """Create a sample benchmark result for report testing."""
    strategy1 = ChunkingStrategy(
        name="fixed_256",
        strategy_type=ChunkingStrategyType.FIXED_SIZE,
        chunk_size=256,
        chunk_overlap=25,
    )
    strategy2 = ChunkingStrategy(
        name="fixed_512",
        strategy_type=ChunkingStrategyType.FIXED_SIZE,
        chunk_size=512,
        chunk_overlap=50,
    )

    metrics1 = RetrievalMetrics(
        mrr=0.85,
        recall_at_1=0.7,
        recall_at_5=0.9,
        recall_at_10=0.95,
        ndcg_at_10=0.88,
        avg_latency_ms=5.5,
        num_queries=10,
        num_chunks=100,
    )
    metrics2 = RetrievalMetrics(
        mrr=0.75,
        recall_at_1=0.6,
        recall_at_5=0.85,
        recall_at_10=0.9,
        ndcg_at_10=0.8,
        avg_latency_ms=4.5,
        num_queries=10,
        num_chunks=50,
    )

    result1 = StrategyResult(
        strategy=strategy1,
        metrics=metrics1,
        query_results=[],
        chunks=[],
    )
    result2 = StrategyResult(
        strategy=strategy2,
        metrics=metrics2,
        query_results=[],
        chunks=[],
    )

    config = BenchmarkConfig(
        name="test_benchmark",
        documents=[Path("doc1.txt"), Path("doc2.txt")],
        queries_file=Path("queries.jsonl"),
        strategies=[strategy1, strategy2],
    )

    return BenchmarkResult(
        config=config,
        strategy_results=[result1, result2],
        best_strategy="fixed_256",
        recommendation="Use fixed_256 for best results.",
        total_time_ms=5000.0,
    )


class TestGenerateHtmlReport:
    """Tests for generate_html_report function."""

    def test_creates_html_file(
        self,
        tmp_path: Path,
        report_result: BenchmarkResult,
    ) -> None:
        """Test that HTML file is created."""
        output_path = tmp_path / "report.html"
        generate_html_report(report_result, output_path)
        assert output_path.exists()

    def test_html_contains_title(
        self,
        tmp_path: Path,
        report_result: BenchmarkResult,
    ) -> None:
        """Test that HTML contains the benchmark name."""
        output_path = tmp_path / "report.html"
        generate_html_report(report_result, output_path)
        content = output_path.read_text()
        assert "test_benchmark" in content

    def test_html_contains_best_strategy(
        self,
        tmp_path: Path,
        report_result: BenchmarkResult,
    ) -> None:
        """Test that HTML contains the best strategy."""
        output_path = tmp_path / "report.html"
        generate_html_report(report_result, output_path)
        content = output_path.read_text()
        assert "fixed_256" in content
        assert "Best" in content

    def test_html_contains_all_strategies(
        self,
        tmp_path: Path,
        report_result: BenchmarkResult,
    ) -> None:
        """Test that HTML contains all strategy names."""
        output_path = tmp_path / "report.html"
        generate_html_report(report_result, output_path)
        content = output_path.read_text()
        assert "fixed_256" in content
        assert "fixed_512" in content

    def test_html_contains_metrics(
        self,
        tmp_path: Path,
        report_result: BenchmarkResult,
    ) -> None:
        """Test that HTML contains metric values."""
        output_path = tmp_path / "report.html"
        generate_html_report(report_result, output_path)
        content = output_path.read_text()
        assert "0.85" in content  # MRR
        assert "MRR" in content

    def test_html_contains_recommendation(
        self,
        tmp_path: Path,
        report_result: BenchmarkResult,
    ) -> None:
        """Test that HTML contains the recommendation."""
        output_path = tmp_path / "report.html"
        generate_html_report(report_result, output_path)
        content = output_path.read_text()
        assert "Use fixed_256 for best results" in content

    def test_creates_parent_directories(
        self,
        tmp_path: Path,
        report_result: BenchmarkResult,
    ) -> None:
        """Test that parent directories are created."""
        output_path = tmp_path / "nested" / "dir" / "report.html"
        generate_html_report(report_result, output_path)
        assert output_path.exists()

    def test_html_is_valid_structure(
        self,
        tmp_path: Path,
        report_result: BenchmarkResult,
    ) -> None:
        """Test that HTML has valid structure."""
        output_path = tmp_path / "report.html"
        generate_html_report(report_result, output_path)
        content = output_path.read_text()
        assert "<!DOCTYPE html>" in content
        assert "<html" in content
        assert "</html>" in content
        assert "<head>" in content
        assert "<body>" in content

    def test_html_contains_plotly(
        self,
        tmp_path: Path,
        report_result: BenchmarkResult,
    ) -> None:
        """Test that HTML includes Plotly for charts."""
        output_path = tmp_path / "report.html"
        generate_html_report(report_result, output_path)
        content = output_path.read_text()
        assert "plotly" in content.lower()
        assert "mrr-chart" in content
        assert "recall-chart" in content

    def test_html_contains_statistics(
        self,
        tmp_path: Path,
        report_result: BenchmarkResult,
    ) -> None:
        """Test that HTML contains summary statistics."""
        output_path = tmp_path / "report.html"
        generate_html_report(report_result, output_path)
        content = output_path.read_text()
        assert "Strategies Tested" in content
        assert "Documents" in content
        assert "Queries" in content
