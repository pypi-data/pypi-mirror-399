"""Configuration loading and validation for Beacon."""

import json
from pathlib import Path
from typing import Any

import yaml

from beacon.models import BenchmarkConfig, ChunkingStrategy, ChunkingStrategyType


def load_config(config_path: Path) -> BenchmarkConfig:
    """Load benchmark configuration from YAML or JSON file."""
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path) as f:
        if config_path.suffix in (".yaml", ".yml"):
            data = yaml.safe_load(f)
        elif config_path.suffix == ".json":
            data = json.load(f)
        else:
            raise ValueError(f"Unsupported config format: {config_path.suffix}")

    return parse_config(data, config_path.parent)


def parse_config(data: dict[str, Any], base_dir: Path) -> BenchmarkConfig:
    """Parse configuration dictionary into BenchmarkConfig."""
    # Parse documents
    documents: list[Path] = []
    for doc_pattern in data.get("documents", []):
        doc_path = base_dir / doc_pattern
        if "*" in doc_pattern:
            documents.extend(doc_path.parent.glob(doc_path.name))
        else:
            documents.append(doc_path)

    # Parse queries file
    queries_file = base_dir / data["queries"]

    # Parse strategies
    strategies: list[ChunkingStrategy] = []
    for strategy_data in data.get("strategies", []):
        strategy = ChunkingStrategy(
            name=strategy_data["name"],
            strategy_type=ChunkingStrategyType(strategy_data["type"]),
            chunk_size=strategy_data.get("chunk_size", 512),
            chunk_overlap=strategy_data.get("overlap", 50),
            params=strategy_data.get("params", {}),
        )
        strategies.append(strategy)

    # Add default strategies if none specified
    if not strategies:
        strategies = get_default_strategies()

    # Parse output directory
    output_dir = Path(data.get("output_dir", "./beacon_results"))
    if not output_dir.is_absolute():
        output_dir = base_dir / output_dir

    return BenchmarkConfig(
        name=data.get("name", "benchmark"),
        documents=documents,
        queries_file=queries_file,
        strategies=strategies,
        embedding_model=data.get("embedding_model", "all-MiniLM-L6-v2"),
        top_k=data.get("top_k", 10),
        output_dir=output_dir,
        cache_embeddings=data.get("cache_embeddings", True),
        generate_html_report=data.get("generate_html_report", True),
        export_csv=data.get("export_csv", True),
        export_json=data.get("export_json", True),
    )


def get_default_strategies() -> list[ChunkingStrategy]:
    """Get default set of chunking strategies to compare."""
    return [
        ChunkingStrategy(
            name="fixed_256",
            strategy_type=ChunkingStrategyType.FIXED_SIZE,
            chunk_size=256,
            chunk_overlap=25,
        ),
        ChunkingStrategy(
            name="fixed_512",
            strategy_type=ChunkingStrategyType.FIXED_SIZE,
            chunk_size=512,
            chunk_overlap=50,
        ),
        ChunkingStrategy(
            name="fixed_1024",
            strategy_type=ChunkingStrategyType.FIXED_SIZE,
            chunk_size=1024,
            chunk_overlap=100,
        ),
        ChunkingStrategy(
            name="sentence",
            strategy_type=ChunkingStrategyType.SENTENCE,
            chunk_size=512,
            chunk_overlap=0,
        ),
        ChunkingStrategy(
            name="recursive",
            strategy_type=ChunkingStrategyType.RECURSIVE,
            chunk_size=512,
            chunk_overlap=50,
        ),
    ]


def create_sample_config(output_path: Path) -> None:
    """Create a sample configuration file."""
    sample_config = {
        "name": "my_benchmark",
        "documents": ["./docs/*.pdf", "./docs/*.txt"],
        "queries": "./queries.jsonl",
        "embedding_model": "all-MiniLM-L6-v2",
        "top_k": 10,
        "output_dir": "./results",
        "strategies": [
            {
                "name": "fixed_256",
                "type": "fixed_size",
                "chunk_size": 256,
                "overlap": 25,
            },
            {
                "name": "fixed_512",
                "type": "fixed_size",
                "chunk_size": 512,
                "overlap": 50,
            },
            {
                "name": "fixed_1024",
                "type": "fixed_size",
                "chunk_size": 1024,
                "overlap": 100,
            },
            {
                "name": "sentence_based",
                "type": "sentence",
                "chunk_size": 512,
                "overlap": 0,
            },
            {
                "name": "recursive",
                "type": "recursive",
                "chunk_size": 512,
                "overlap": 50,
            },
        ],
        "cache_embeddings": True,
        "generate_html_report": True,
        "export_csv": True,
        "export_json": True,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        yaml.dump(sample_config, f, default_flow_style=False, sort_keys=False)
