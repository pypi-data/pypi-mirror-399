"""Tests for embedding generation."""

import numpy as np
import pytest
from pathlib import Path
from unittest.mock import MagicMock

from beacon.embeddings import EmbeddingGenerator
from beacon.models import Chunk, Query


class TestEmbeddingGeneratorInit:
    """Tests for EmbeddingGenerator initialization."""

    def test_default_init(self) -> None:
        """Test default initialization."""
        gen = EmbeddingGenerator()
        assert gen.model_name == "all-MiniLM-L6-v2"
        assert gen.cache_dir is None
        assert gen.batch_size == 32

    def test_custom_init(self, tmp_path: Path) -> None:
        """Test custom initialization."""
        gen = EmbeddingGenerator(
            model_name="custom-model",
            cache_dir=tmp_path,
            batch_size=64,
        )
        assert gen.model_name == "custom-model"
        assert gen.cache_dir == tmp_path
        assert gen.batch_size == 64


class TestEmbeddingGeneratorCaching:
    """Tests for embedding caching."""

    def test_cache_key_generation(self, sample_chunks: list[Chunk]) -> None:
        """Test that cache key is generated correctly."""
        gen = EmbeddingGenerator()
        key = gen._get_cache_key(sample_chunks)
        assert isinstance(key, str)
        assert len(key) == 16  # SHA256 truncated to 16 chars

    def test_cache_key_different_for_different_chunks(
        self,
        sample_chunks: list[Chunk],
    ) -> None:
        """Test that different chunks produce different cache keys."""
        gen = EmbeddingGenerator()
        key1 = gen._get_cache_key(sample_chunks)
        key2 = gen._get_cache_key([sample_chunks[0]])
        assert key1 != key2

    def test_cache_key_different_for_different_models(
        self,
        sample_chunks: list[Chunk],
    ) -> None:
        """Test that different models produce different cache keys."""
        gen1 = EmbeddingGenerator(model_name="model1")
        gen2 = EmbeddingGenerator(model_name="model2")
        key1 = gen1._get_cache_key(sample_chunks)
        key2 = gen2._get_cache_key(sample_chunks)
        assert key1 != key2

    def test_save_and_load_cache(self, tmp_path: Path) -> None:
        """Test saving and loading from cache."""
        gen = EmbeddingGenerator(cache_dir=tmp_path)
        cache_key = "test_key"
        embeddings = np.random.randn(5, 128).astype(np.float32)

        gen._save_to_cache(cache_key, embeddings)
        loaded = gen._load_from_cache(cache_key)

        assert loaded is not None
        np.testing.assert_array_almost_equal(embeddings, loaded)

    def test_load_from_cache_not_found(self, tmp_path: Path) -> None:
        """Test loading from cache when not found."""
        gen = EmbeddingGenerator(cache_dir=tmp_path)
        loaded = gen._load_from_cache("nonexistent_key")
        assert loaded is None

    def test_load_from_cache_no_cache_dir(self) -> None:
        """Test loading from cache with no cache dir."""
        gen = EmbeddingGenerator(cache_dir=None)
        loaded = gen._load_from_cache("any_key")
        assert loaded is None

    def test_save_to_cache_creates_dir(self, tmp_path: Path) -> None:
        """Test that cache dir is created if it doesn't exist."""
        cache_dir = tmp_path / "nested" / "cache"
        gen = EmbeddingGenerator(cache_dir=cache_dir)
        embeddings = np.random.randn(2, 64).astype(np.float32)

        gen._save_to_cache("test", embeddings)
        assert cache_dir.exists()


class TestEmbeddingGeneratorWithModel:
    """Tests that require the actual model (integration tests)."""

    @pytest.fixture
    def mock_model(self) -> MagicMock:
        """Create a mock sentence transformer model."""
        mock = MagicMock()
        mock.encode.return_value = np.random.randn(2, 384).astype(np.float32)
        mock.get_sentence_embedding_dimension.return_value = 384
        return mock

    def test_embed_chunks_with_mock(
        self,
        sample_chunks: list[Chunk],
        mock_model: MagicMock,
    ) -> None:
        """Test embedding chunks with mocked model."""
        gen = EmbeddingGenerator()
        gen._model = mock_model

        embeddings = gen.embed_chunks(sample_chunks, show_progress=False, use_cache=False)

        assert embeddings.shape[0] == 2
        mock_model.encode.assert_called_once()

    def test_embed_queries_with_mock(
        self,
        sample_queries: list[Query],
        mock_model: MagicMock,
    ) -> None:
        """Test embedding queries with mocked model."""
        gen = EmbeddingGenerator()
        gen._model = mock_model

        embeddings = gen.embed_queries(sample_queries, show_progress=False)

        assert embeddings.shape[0] == 2
        mock_model.encode.assert_called_once()

    def test_embed_text_with_mock(self, mock_model: MagicMock) -> None:
        """Test embedding single text with mocked model."""
        mock_model.encode.return_value = np.array([[0.1, 0.2, 0.3]])
        gen = EmbeddingGenerator()
        gen._model = mock_model

        embedding = gen.embed_text("test text")

        assert len(embedding) == 3
        mock_model.encode.assert_called_with(["test text"], show_progress_bar=False)

    def test_embedding_dimension_with_mock(self, mock_model: MagicMock) -> None:
        """Test getting embedding dimension."""
        gen = EmbeddingGenerator()
        gen._model = mock_model

        dim = gen.embedding_dimension
        assert dim == 384

    def test_uses_cache_when_available(
        self,
        tmp_path: Path,
        sample_chunks: list[Chunk],
        mock_model: MagicMock,
    ) -> None:
        """Test that cached embeddings are used when available."""
        gen = EmbeddingGenerator(cache_dir=tmp_path)
        gen._model = mock_model

        # First call should generate and cache
        mock_model.encode.return_value = np.random.randn(2, 384).astype(np.float32)
        gen.embed_chunks(sample_chunks, show_progress=False, use_cache=True)
        assert mock_model.encode.call_count == 1

        # Second call should use cache
        gen.embed_chunks(sample_chunks, show_progress=False, use_cache=True)
        assert mock_model.encode.call_count == 1  # Still 1, not called again

    def test_skips_cache_when_disabled(
        self,
        tmp_path: Path,
        sample_chunks: list[Chunk],
        mock_model: MagicMock,
    ) -> None:
        """Test that cache is skipped when disabled."""
        gen = EmbeddingGenerator(cache_dir=tmp_path)
        gen._model = mock_model
        mock_model.encode.return_value = np.random.randn(2, 384).astype(np.float32)

        # First call
        gen.embed_chunks(sample_chunks, show_progress=False, use_cache=False)
        # Second call with cache disabled
        gen.embed_chunks(sample_chunks, show_progress=False, use_cache=False)

        assert mock_model.encode.call_count == 2


class TestEmbeddingGeneratorBatching:
    """Tests for batch processing."""

    def test_large_batch_processing(self) -> None:
        """Test processing many chunks in batches."""
        mock_model = MagicMock()
        # Return different shaped arrays for each batch
        mock_model.encode.side_effect = [
            np.random.randn(32, 384).astype(np.float32),
            np.random.randn(32, 384).astype(np.float32),
            np.random.randn(6, 384).astype(np.float32),  # Last batch
        ]
        mock_model.get_sentence_embedding_dimension.return_value = 384

        gen = EmbeddingGenerator(batch_size=32)
        gen._model = mock_model

        # Create 70 chunks
        chunks = [
            Chunk(
                text=f"Chunk {i}",
                doc_id="doc",
                chunk_id=f"chunk_{i}",
                start_char=0,
                end_char=10,
                token_count=2,
            )
            for i in range(70)
        ]

        embeddings = gen.embed_chunks(chunks, show_progress=False, use_cache=False)

        # Should call encode 3 times (32 + 32 + 6)
        assert mock_model.encode.call_count == 3
        assert embeddings.shape == (70, 384)
