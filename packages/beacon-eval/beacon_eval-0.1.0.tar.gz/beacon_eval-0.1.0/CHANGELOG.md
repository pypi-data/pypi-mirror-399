# Changelog

All notable changes to Beacon will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-01

### Added
- Initial release
- 5 chunking strategies: fixed-size, sentence, paragraph, recursive, semantic
- Support for multiple document formats: TXT, MD, PDF, DOCX, JSON
- Embedding generation with sentence-transformers
- FAISS vector indexing for fast retrieval
- Comprehensive retrieval metrics: MRR, Recall@k, Precision@k, NDCG, MAP
- Multiple output formats: JSON, CSV, HTML reports
- CLI with commands: init, run, strategies, compare
- Bayesian optimization for auto-tuning chunk parameters (optional)
- Embedding caching for faster repeated benchmarks
