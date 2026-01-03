# Beacon

**A benchmarking toolkit that evaluates and compares RAG chunking strategies against your actual queries to find the optimal configuration.**

[![PyPI](https://img.shields.io/pypi/v/beacon-eval)](https://pypi.org/project/beacon-eval/)
[![CI](https://img.shields.io/github/actions/workflow/status/en-yao/beacon-eval/ci.yml)](https://github.com/en-yao/beacon-eval/actions)
[![Python](https://img.shields.io/pypi/pyversions/beacon-eval)](https://pypi.org/project/beacon-eval/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## Why Beacon?

RAG quality is 80% retrieval quality, and retrieval quality depends heavily on chunking. Yet most teams:

- Use default chunk sizes (512 tokens) without evaluation
- Don't know if semantic chunking would improve their specific use case
- Spend weeks manually testing different configurations
- Have no metrics to compare strategies objectively

**Beacon automates this with reproducible benchmarks.**

## Features

- **Multi-Strategy Evaluation** - Compare 5+ chunking strategies in one run
- **Standard IR Metrics** - MRR, Recall@K, NDCG, Precision, MAP
- **Bayesian Auto-Tuning** - Find optimal chunk size and overlap automatically
- **HTML Reports** - Beautiful, shareable benchmark reports
- **Local-First** - Run entirely offline with local embeddings
- **Framework Agnostic** - Works with any RAG implementation

## Installation

```bash
pip install beacon-eval
```

For auto-tuning support:

```bash
pip install beacon-eval[optuna]
```

## Quick Start

### 1. Create a configuration file

```bash
beacon init
```

This creates a `beacon.yaml` configuration file.

### 2. Prepare your queries

Create a `queries.jsonl` file with your test queries:

```jsonl
{"query": "What is the refund policy?", "relevant_doc_ids": ["policy.pdf"]}
{"query": "How do I reset my password?", "relevant_doc_ids": ["faq.pdf"]}
```

### 3. Run the benchmark

```bash
beacon run beacon.yaml
```

## Configuration

```yaml
name: my_benchmark
documents:
  - ./docs/*.pdf
  - ./docs/*.txt
queries: ./queries.jsonl
embedding_model: all-MiniLM-L6-v2
top_k: 10

strategies:
  - name: fixed_256
    type: fixed_size
    chunk_size: 256
    overlap: 25

  - name: fixed_512
    type: fixed_size
    chunk_size: 512
    overlap: 50

  - name: sentence_based
    type: sentence
    chunk_size: 512

  - name: recursive
    type: recursive
    chunk_size: 512
    overlap: 50

output_dir: ./results
generate_html_report: true
export_csv: true
```

## Chunking Strategies

| Strategy | Description |
|----------|-------------|
| `fixed_size` | Split by fixed token/character count |
| `sentence` | Split by sentence boundaries |
| `paragraph` | Split by paragraph boundaries |
| `semantic` | Split by semantic similarity |
| `recursive` | Recursively split with multiple separators |

## Python API

```python
from beacon import BenchmarkConfig, ChunkingStrategy
from beacon.runner import run_benchmark
from beacon.parsers import load_documents, load_queries

# Load your data
documents = load_documents([Path("./docs")])
queries = load_queries(Path("./queries.jsonl"))

# Define strategies
strategies = [
    ChunkingStrategy(name="small", strategy_type="fixed_size", chunk_size=256),
    ChunkingStrategy(name="medium", strategy_type="fixed_size", chunk_size=512),
    ChunkingStrategy(name="large", strategy_type="fixed_size", chunk_size=1024),
]

# Run benchmark
config = BenchmarkConfig(
    name="my_benchmark",
    documents=[Path("./docs")],
    queries_file=Path("./queries.jsonl"),
    strategies=strategies,
)

result = run_benchmark(config)
print(f"Best strategy: {result.best_strategy}")
```

## Auto-Tuning

Find optimal chunking parameters automatically:

```python
from beacon.tuner import auto_tune
from beacon.parsers import load_documents, load_queries
from beacon.models import ChunkingStrategyType

documents = load_documents([Path("./docs")])
queries = load_queries(Path("./queries.jsonl"))

result = auto_tune(
    documents=documents,
    queries=queries,
    strategy_type=ChunkingStrategyType.FIXED_SIZE,
    metric="mrr",
    n_trials=50,
    chunk_size_range=(100, 2000),
)

print(f"Optimal chunk size: {result['chunk_size']}")
print(f"Optimal overlap: {result['chunk_overlap']}")
print(f"Best MRR: {result['best_mrr']:.4f}")
```

## Metrics

| Metric | Description | Good Score |
|--------|-------------|------------|
| MRR | Mean Reciprocal Rank | > 0.7 |
| Recall@K | % of relevant docs in top K | > 0.8 |
| NDCG@K | Normalized DCG | > 0.75 |
| Precision@K | Precision at K | > 0.6 |
| MAP | Mean Average Precision | > 0.6 |

## CLI Commands

```bash
# Initialize sample configuration
beacon init

# Run benchmark
beacon run config.yaml

# List available strategies
beacon strategies

# Compare multiple benchmark results
beacon compare results1.json results2.json
```

## Output

Beacon generates:

- **`results.json`** - Full results in JSON format
- **`results.csv`** - Comparison table in CSV
- **`report.html`** - Interactive HTML report with charts

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Security

If you discover a security vulnerability, please see [SECURITY.md](SECURITY.md) for reporting guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.
