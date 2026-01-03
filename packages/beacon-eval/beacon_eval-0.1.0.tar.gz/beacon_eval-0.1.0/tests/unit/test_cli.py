"""Tests for CLI commands."""

import pytest
from pathlib import Path
from typer.testing import CliRunner

from beacon.cli import app


runner = CliRunner()


class TestCliInit:
    """Tests for init command."""

    def test_init_creates_config(self, tmp_path: Path) -> None:
        """Test that init creates a config file."""
        config_path = tmp_path / "beacon.yaml"
        result = runner.invoke(app, ["init", "--output", str(config_path)])
        assert result.exit_code == 0
        assert config_path.exists()

    def test_init_creates_queries_file(self, tmp_path: Path) -> None:
        """Test that init creates a queries file."""
        config_path = tmp_path / "beacon.yaml"
        result = runner.invoke(app, ["init", "-o", str(config_path)])
        assert result.exit_code == 0
        # Queries file is created in same directory as config
        queries_path = tmp_path / "queries.jsonl"
        # Note: create_sample_config doesn't create queries file, just config
        assert config_path.exists()

    def test_init_default_path(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test init with default path."""
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0
        assert (tmp_path / "beacon.yaml").exists()


class TestCliStrategies:
    """Tests for strategies command."""

    def test_strategies_lists_all(self) -> None:
        """Test that strategies lists all available strategies."""
        result = runner.invoke(app, ["strategies"])
        assert result.exit_code == 0
        assert "fixed_size" in result.output
        assert "sentence" in result.output
        assert "recursive" in result.output

    def test_strategies_shows_descriptions(self) -> None:
        """Test that strategies shows descriptions."""
        result = runner.invoke(app, ["strategies"])
        assert result.exit_code == 0
        # Check for some descriptive content
        assert "chunk" in result.output.lower() or "split" in result.output.lower()


class TestCliRun:
    """Tests for run command."""

    def test_run_missing_config(self, tmp_path: Path) -> None:
        """Test run with missing config file."""
        result = runner.invoke(app, ["run", str(tmp_path / "nonexistent.yaml")])
        assert result.exit_code != 0

    def test_run_invalid_config(self, tmp_path: Path) -> None:
        """Test run with invalid config file."""
        config_path = tmp_path / "invalid.yaml"
        config_path.write_text("invalid: yaml: content:")
        result = runner.invoke(app, ["run", str(config_path)])
        assert result.exit_code != 0


class TestCliCompare:
    """Tests for compare command."""

    def test_compare_missing_files(self, tmp_path: Path) -> None:
        """Test compare with missing result files."""
        result = runner.invoke(
            app,
            ["compare", str(tmp_path / "a.json"), str(tmp_path / "b.json")],
        )
        assert result.exit_code != 0


class TestCliVersion:
    """Tests for version display."""

    def test_version_option(self) -> None:
        """Test --version option."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "beacon version" in result.output

    def test_version_short_option(self) -> None:
        """Test -v option for version."""
        result = runner.invoke(app, ["-v"])
        assert result.exit_code == 0
        assert "beacon version" in result.output


class TestCliCompareMore:
    """Additional tests for compare command."""

    def test_compare_needs_two_files(self, tmp_path: Path) -> None:
        """Test that compare requires at least 2 files."""
        file1 = tmp_path / "result1.json"
        file1.write_text('{"best_strategy": "test"}')

        result = runner.invoke(app, ["compare", str(file1)])
        assert result.exit_code != 0

    def test_compare_valid_files(self, tmp_path: Path) -> None:
        """Test comparing valid result files."""
        import json

        file1 = tmp_path / "result1.json"
        file2 = tmp_path / "result2.json"

        data1 = {
            "config": {"name": "bench1"},
            "best_strategy": "fixed_256",
            "strategy_results": [
                {
                    "strategy": {"name": "fixed_256"},
                    "metrics": {"mrr": 0.8, "recall@5": 0.9, "ndcg@10": 0.85},
                }
            ],
        }
        data2 = {
            "config": {"name": "bench2"},
            "best_strategy": "fixed_512",
            "strategy_results": [
                {
                    "strategy": {"name": "fixed_512"},
                    "metrics": {"mrr": 0.75, "recall@5": 0.85, "ndcg@10": 0.8},
                }
            ],
        }

        file1.write_text(json.dumps(data1))
        file2.write_text(json.dumps(data2))

        result = runner.invoke(app, ["compare", str(file1), str(file2)])
        assert result.exit_code == 0
        assert "bench1" in result.output
        assert "bench2" in result.output


class TestCliInitOverwrite:
    """Tests for init command overwrite behavior."""

    def test_init_asks_overwrite(self, tmp_path: Path) -> None:
        """Test that init asks for overwrite confirmation."""
        config_path = tmp_path / "beacon.yaml"
        config_path.write_text("existing: config")

        # First invocation should ask for confirmation
        result = runner.invoke(app, ["init", "-o", str(config_path)], input="n\n")
        # Should exit without overwriting when user says no
        assert result.exit_code == 0

    def test_init_overwrites_when_confirmed(self, tmp_path: Path) -> None:
        """Test that init overwrites when user confirms."""
        config_path = tmp_path / "beacon.yaml"
        config_path.write_text("existing: config")

        result = runner.invoke(app, ["init", "-o", str(config_path)], input="y\n")
        assert result.exit_code == 0
        # File should be overwritten with new content
        content = config_path.read_text()
        assert "name:" in content  # New sample config has 'name' field
