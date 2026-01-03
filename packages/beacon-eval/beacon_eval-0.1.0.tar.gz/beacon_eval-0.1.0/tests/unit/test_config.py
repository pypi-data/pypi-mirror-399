"""Tests for configuration loading and validation."""

import pytest
from pathlib import Path
import tempfile
import json

import yaml

from beacon.config import (
    get_default_strategies,
    load_config,
    parse_config,
    create_sample_config,
)
from beacon.models import ChunkingStrategyType


class TestGetDefaultStrategies:
    """Tests for get_default_strategies function."""

    def test_returns_list(self) -> None:
        """Test that default strategies returns a list."""
        strategies = get_default_strategies()
        assert isinstance(strategies, list)
        assert len(strategies) > 0

    def test_strategy_names(self) -> None:
        """Test that strategies have expected names."""
        strategies = get_default_strategies()
        names = [s.name for s in strategies]
        assert "fixed_256" in names
        assert "fixed_512" in names
        assert "fixed_1024" in names
        assert "sentence" in names
        assert "recursive" in names

    def test_strategy_types(self) -> None:
        """Test that strategies have valid types."""
        strategies = get_default_strategies()
        types = [s.strategy_type for s in strategies]
        assert ChunkingStrategyType.FIXED_SIZE in types
        assert ChunkingStrategyType.SENTENCE in types
        assert ChunkingStrategyType.RECURSIVE in types

    def test_chunk_sizes_vary(self) -> None:
        """Test that chunk sizes vary across strategies."""
        strategies = get_default_strategies()
        sizes = {s.chunk_size for s in strategies}
        assert len(sizes) > 1  # Multiple different sizes


class TestLoadConfig:
    """Tests for load_config function."""

    def test_file_not_found(self) -> None:
        """Test error when config file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            load_config(Path("/nonexistent/config.yaml"))

    def test_load_yaml_config(self, tmp_path: Path) -> None:
        """Test loading YAML config file."""
        config_data = {
            "name": "test_benchmark",
            "documents": [],
            "queries": "queries.jsonl",
            "strategies": [
                {
                    "name": "test_fixed",
                    "type": "fixed_size",
                    "chunk_size": 256,
                    "overlap": 25,
                }
            ],
        }
        config_path = tmp_path / "config.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        # Create queries file
        queries_path = tmp_path / "queries.jsonl"
        queries_path.touch()

        config = load_config(config_path)
        assert config.name == "test_benchmark"
        assert len(config.strategies) == 1
        assert config.strategies[0].name == "test_fixed"

    def test_load_json_config(self, tmp_path: Path) -> None:
        """Test loading JSON config file."""
        config_data = {
            "name": "json_benchmark",
            "documents": [],
            "queries": "queries.jsonl",
            "strategies": [],
        }
        config_path = tmp_path / "config.json"
        with open(config_path, "w") as f:
            json.dump(config_data, f)

        # Create queries file
        queries_path = tmp_path / "queries.jsonl"
        queries_path.touch()

        config = load_config(config_path)
        assert config.name == "json_benchmark"

    def test_unsupported_format(self, tmp_path: Path) -> None:
        """Test error on unsupported config format."""
        config_path = tmp_path / "config.txt"
        config_path.write_text("invalid")

        with pytest.raises(ValueError, match="Unsupported config format"):
            load_config(config_path)


class TestParseConfig:
    """Tests for parse_config function."""

    def test_parse_minimal_config(self, tmp_path: Path) -> None:
        """Test parsing minimal config."""
        # Create queries file
        queries_path = tmp_path / "queries.jsonl"
        queries_path.touch()

        data = {
            "queries": "queries.jsonl",
        }
        config = parse_config(data, tmp_path)
        assert config.name == "benchmark"  # Default name
        assert len(config.strategies) > 0  # Default strategies added

    def test_parse_with_glob_pattern(self, tmp_path: Path) -> None:
        """Test parsing config with glob patterns in documents."""
        # Create test files
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "file1.txt").write_text("content1")
        (docs_dir / "file2.txt").write_text("content2")

        queries_path = tmp_path / "queries.jsonl"
        queries_path.touch()

        data = {
            "documents": ["docs/*.txt"],
            "queries": "queries.jsonl",
        }
        config = parse_config(data, tmp_path)
        assert len(config.documents) == 2

    def test_parse_custom_embedding_model(self, tmp_path: Path) -> None:
        """Test parsing config with custom embedding model."""
        queries_path = tmp_path / "queries.jsonl"
        queries_path.touch()

        data = {
            "queries": "queries.jsonl",
            "embedding_model": "custom-model",
        }
        config = parse_config(data, tmp_path)
        assert config.embedding_model == "custom-model"

    def test_parse_custom_top_k(self, tmp_path: Path) -> None:
        """Test parsing config with custom top_k."""
        queries_path = tmp_path / "queries.jsonl"
        queries_path.touch()

        data = {
            "queries": "queries.jsonl",
            "top_k": 20,
        }
        config = parse_config(data, tmp_path)
        assert config.top_k == 20

    def test_parse_output_settings(self, tmp_path: Path) -> None:
        """Test parsing output settings."""
        queries_path = tmp_path / "queries.jsonl"
        queries_path.touch()

        data = {
            "queries": "queries.jsonl",
            "cache_embeddings": False,
            "generate_html_report": False,
            "export_csv": False,
            "export_json": False,
        }
        config = parse_config(data, tmp_path)
        assert config.cache_embeddings is False
        assert config.generate_html_report is False
        assert config.export_csv is False
        assert config.export_json is False


class TestCreateSampleConfig:
    """Tests for create_sample_config function."""

    def test_creates_file(self, tmp_path: Path) -> None:
        """Test that sample config file is created."""
        output_path = tmp_path / "sample.yaml"
        create_sample_config(output_path)
        assert output_path.exists()

    def test_creates_valid_yaml(self, tmp_path: Path) -> None:
        """Test that created file is valid YAML."""
        output_path = tmp_path / "sample.yaml"
        create_sample_config(output_path)

        with open(output_path) as f:
            data = yaml.safe_load(f)

        assert "name" in data
        assert "documents" in data
        assert "queries" in data
        assert "strategies" in data

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Test that parent directories are created."""
        output_path = tmp_path / "nested" / "dir" / "config.yaml"
        create_sample_config(output_path)
        assert output_path.exists()

    def test_sample_has_multiple_strategies(self, tmp_path: Path) -> None:
        """Test that sample config has multiple strategies."""
        output_path = tmp_path / "sample.yaml"
        create_sample_config(output_path)

        with open(output_path) as f:
            data = yaml.safe_load(f)

        assert len(data["strategies"]) >= 3
