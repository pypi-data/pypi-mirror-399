"""Sample benchmark script demonstrating Beacon usage."""

from pathlib import Path

from beacon.config import get_default_strategies
from beacon.models import BenchmarkConfig, Document, Query
from beacon.runner import run_benchmark


def main() -> None:
    """Run a sample benchmark."""
    # Create sample documents
    documents = [
        Document(
            doc_id="doc1",
            content="""
            Machine learning is a subset of artificial intelligence that enables
            systems to learn and improve from experience without being explicitly
            programmed. It focuses on developing computer programs that can access
            data and use it to learn for themselves.
            """,
        ),
        Document(
            doc_id="doc2",
            content="""
            Deep learning is part of a broader family of machine learning methods
            based on artificial neural networks with representation learning.
            Learning can be supervised, semi-supervised or unsupervised.
            """,
        ),
        Document(
            doc_id="doc3",
            content="""
            Natural language processing (NLP) is a field of computer science and
            artificial intelligence concerned with the interactions between
            computers and human language. It involves programming computers to
            process and analyze large amounts of natural language data.
            """,
        ),
    ]

    # Create sample queries
    queries = [
        Query(
            query_id="q1",
            text="What is machine learning?",
            relevant_doc_ids=["doc1"],
        ),
        Query(
            query_id="q2",
            text="How does deep learning work?",
            relevant_doc_ids=["doc2"],
        ),
        Query(
            query_id="q3",
            text="What is NLP used for?",
            relevant_doc_ids=["doc3"],
        ),
    ]

    # Get default strategies
    strategies = get_default_strategies()

    # Create benchmark config
    config = BenchmarkConfig(
        name="sample_benchmark",
        documents=[],  # We'll use documents directly
        queries_file=Path("queries.jsonl"),  # Placeholder
        strategies=strategies,
        output_dir=Path("./sample_results"),
    )

    print("Running sample benchmark...")
    print(f"Documents: {len(documents)}")
    print(f"Queries: {len(queries)}")
    print(f"Strategies: {len(strategies)}")
    print()

    # Note: This is a simplified example. In practice, you would use
    # the full run_benchmark() function with file-based documents and queries.

    print("To run a full benchmark, use:")
    print("  beacon init  # Create config file")
    print("  beacon run beacon.yaml  # Run benchmark")


if __name__ == "__main__":
    main()
