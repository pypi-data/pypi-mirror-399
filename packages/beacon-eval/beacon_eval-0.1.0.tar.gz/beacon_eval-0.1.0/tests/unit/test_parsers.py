"""Tests for document parsing utilities."""

import json
import pytest
from pathlib import Path

from beacon.parsers import (
    load_document,
    load_documents,
    load_queries,
    create_sample_queries,
)


class TestLoadDocument:
    """Tests for load_document function."""

    def test_load_text_file(self, tmp_path: Path) -> None:
        """Test loading a plain text file."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("Hello, world!", encoding="utf-8")

        doc = load_document(file_path)
        assert doc.doc_id == "test"
        assert doc.content == "Hello, world!"
        assert doc.source_path == file_path
        assert doc.metadata["file_type"] == ".txt"

    def test_load_markdown_file(self, tmp_path: Path) -> None:
        """Test loading a markdown file."""
        file_path = tmp_path / "readme.md"
        file_path.write_text("# Title\n\nContent here.", encoding="utf-8")

        doc = load_document(file_path)
        assert doc.doc_id == "readme"
        assert "# Title" in doc.content
        assert doc.metadata["file_type"] == ".md"

    def test_load_json_with_content_field(self, tmp_path: Path) -> None:
        """Test loading JSON file with content field."""
        file_path = tmp_path / "doc.json"
        data = {"content": "This is the content", "title": "Test"}
        file_path.write_text(json.dumps(data), encoding="utf-8")

        doc = load_document(file_path)
        assert doc.content == "This is the content"

    def test_load_json_with_text_field(self, tmp_path: Path) -> None:
        """Test loading JSON file with text field."""
        file_path = tmp_path / "doc.json"
        data = {"text": "Text content here"}
        file_path.write_text(json.dumps(data), encoding="utf-8")

        doc = load_document(file_path)
        assert doc.content == "Text content here"

    def test_load_json_serializes_unknown(self, tmp_path: Path) -> None:
        """Test that unknown JSON structure is serialized."""
        file_path = tmp_path / "doc.json"
        data = {"unknown_field": "value", "another": 123}
        file_path.write_text(json.dumps(data), encoding="utf-8")

        doc = load_document(file_path)
        assert "unknown_field" in doc.content

    def test_file_not_found(self) -> None:
        """Test error when file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            load_document(Path("/nonexistent/file.txt"))

    def test_loads_unknown_extension_as_text(self, tmp_path: Path) -> None:
        """Test that unknown extensions are loaded as text."""
        file_path = tmp_path / "file.xyz"
        file_path.write_text("Some content")

        doc = load_document(file_path)
        assert doc.content == "Some content"

    def test_metadata_includes_file_size(self, tmp_path: Path) -> None:
        """Test that file size is included in metadata."""
        file_path = tmp_path / "test.txt"
        content = "Test content"
        file_path.write_text(content, encoding="utf-8")

        doc = load_document(file_path)
        assert "file_size" in doc.metadata
        assert doc.metadata["file_size"] > 0


class TestLoadDocuments:
    """Tests for load_documents function."""

    def test_load_multiple_files(self, tmp_path: Path) -> None:
        """Test loading multiple documents."""
        (tmp_path / "doc1.txt").write_text("Content 1")
        (tmp_path / "doc2.txt").write_text("Content 2")

        docs = load_documents([tmp_path / "doc1.txt", tmp_path / "doc2.txt"])
        assert len(docs) == 2

    def test_load_from_directory(self, tmp_path: Path) -> None:
        """Test loading all documents from a directory."""
        (tmp_path / "doc1.txt").write_text("Content 1")
        (tmp_path / "doc2.md").write_text("Content 2")
        (tmp_path / "ignored.py").write_text("# Python file")

        docs = load_documents([tmp_path])
        assert len(docs) == 2  # Only .txt and .md

    def test_empty_paths_list(self) -> None:
        """Test with empty paths list."""
        docs = load_documents([])
        assert len(docs) == 0


class TestLoadQueries:
    """Tests for load_queries function."""

    def test_load_queries(self, tmp_path: Path) -> None:
        """Test loading queries from JSONL file."""
        queries_file = tmp_path / "queries.jsonl"
        lines = [
            json.dumps({"query_id": "q1", "query": "First query", "relevant_doc_ids": ["d1"]}),
            json.dumps({"query_id": "q2", "query": "Second query", "relevant_doc_ids": ["d2"]}),
        ]
        queries_file.write_text("\n".join(lines), encoding="utf-8")

        queries = load_queries(queries_file)
        assert len(queries) == 2
        assert queries[0].query_id == "q1"
        assert queries[0].text == "First query"
        assert queries[0].relevant_doc_ids == ["d1"]

    def test_auto_generate_query_id(self, tmp_path: Path) -> None:
        """Test that query_id is auto-generated if not provided."""
        queries_file = tmp_path / "queries.jsonl"
        line = json.dumps({"query": "Test query"})
        queries_file.write_text(line, encoding="utf-8")

        queries = load_queries(queries_file)
        assert queries[0].query_id == "q1"

    def test_skip_empty_lines(self, tmp_path: Path) -> None:
        """Test that empty lines are skipped."""
        queries_file = tmp_path / "queries.jsonl"
        lines = [
            json.dumps({"query": "Query 1"}),
            "",
            json.dumps({"query": "Query 2"}),
        ]
        queries_file.write_text("\n".join(lines), encoding="utf-8")

        queries = load_queries(queries_file)
        assert len(queries) == 2

    def test_file_not_found(self) -> None:
        """Test error when queries file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            load_queries(Path("/nonexistent/queries.jsonl"))

    def test_invalid_json(self, tmp_path: Path) -> None:
        """Test error on invalid JSON."""
        queries_file = tmp_path / "queries.jsonl"
        queries_file.write_text("not valid json", encoding="utf-8")

        with pytest.raises(ValueError, match="Error parsing query"):
            load_queries(queries_file)

    def test_missing_query_field(self, tmp_path: Path) -> None:
        """Test error when query field is missing."""
        queries_file = tmp_path / "queries.jsonl"
        line = json.dumps({"query_id": "q1"})  # Missing "query" field
        queries_file.write_text(line, encoding="utf-8")

        with pytest.raises(ValueError, match="Error parsing query"):
            load_queries(queries_file)

    def test_load_with_metadata(self, tmp_path: Path) -> None:
        """Test loading queries with metadata."""
        queries_file = tmp_path / "queries.jsonl"
        line = json.dumps({
            "query": "Test",
            "metadata": {"category": "test", "priority": 1},
        })
        queries_file.write_text(line, encoding="utf-8")

        queries = load_queries(queries_file)
        assert queries[0].metadata["category"] == "test"
        assert queries[0].metadata["priority"] == 1

    def test_load_with_chunk_ids(self, tmp_path: Path) -> None:
        """Test loading queries with relevant chunk IDs."""
        queries_file = tmp_path / "queries.jsonl"
        line = json.dumps({
            "query": "Test",
            "relevant_chunk_ids": ["c1", "c2"],
        })
        queries_file.write_text(line, encoding="utf-8")

        queries = load_queries(queries_file)
        assert queries[0].relevant_chunk_ids == ["c1", "c2"]


class TestCreateSampleQueries:
    """Tests for create_sample_queries function."""

    def test_creates_file(self, tmp_path: Path) -> None:
        """Test that sample queries file is created."""
        output_path = tmp_path / "queries.jsonl"
        create_sample_queries(output_path)
        assert output_path.exists()

    def test_creates_valid_jsonl(self, tmp_path: Path) -> None:
        """Test that created file is valid JSONL."""
        output_path = tmp_path / "queries.jsonl"
        create_sample_queries(output_path)

        with open(output_path) as f:
            lines = f.readlines()

        assert len(lines) >= 1
        for line in lines:
            data = json.loads(line)
            assert "query" in data
            assert "query_id" in data

    def test_uses_provided_doc_ids(self, tmp_path: Path) -> None:
        """Test that provided doc IDs are used."""
        output_path = tmp_path / "queries.jsonl"
        create_sample_queries(output_path, doc_ids=["my_doc1", "my_doc2"])

        with open(output_path) as f:
            lines = f.readlines()

        data = json.loads(lines[0])
        assert "my_doc1" in data["relevant_doc_ids"]

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Test that parent directories are created."""
        output_path = tmp_path / "nested" / "dir" / "queries.jsonl"
        create_sample_queries(output_path)
        assert output_path.exists()
