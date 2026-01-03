"""Embedding generation for chunks and queries."""

import contextlib
import hashlib
import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import numpy as np
import numpy.typing as npt
from tqdm import tqdm

from beacon.models import Chunk, Query

# Type alias for numpy arrays
NDArrayFloat = npt.NDArray[np.floating[Any]]


class EmbeddingGenerator:
    """Generate embeddings for chunks and queries using sentence-transformers."""

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        cache_dir: Path | None = None,
        batch_size: int = 32,
    ) -> None:
        """Initialize the embedding generator.

        Args:
            model_name: Name of the sentence-transformers model.
            cache_dir: Directory to cache embeddings.
            batch_size: Batch size for embedding generation.
        """
        self.model_name = model_name
        self.cache_dir = cache_dir
        self.batch_size = batch_size
        self._model: Any = None

    def _get_model(self) -> Any:
        """Lazy load the embedding model."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer

                self._model = SentenceTransformer(self.model_name)
            except ImportError as err:
                raise ImportError(
                    "sentence-transformers is required for embeddings. "
                    "Install with: pip install sentence-transformers"
                ) from err
        return self._model

    def embed_chunks(
        self,
        chunks: list[Chunk],
        show_progress: bool = True,
        use_cache: bool = True,
    ) -> NDArrayFloat:
        """Generate embeddings for a list of chunks.

        Args:
            chunks: List of chunks to embed.
            show_progress: Whether to show progress bar.
            use_cache: Whether to use cached embeddings.

        Returns:
            numpy array of embeddings with shape (num_chunks, embedding_dim).
        """
        # Check cache first
        if use_cache and self.cache_dir:
            cache_key = self._get_cache_key(chunks)
            cached = self._load_from_cache(cache_key)
            if cached is not None:
                return cached

        # Generate embeddings
        texts = [chunk.text for chunk in chunks]
        embeddings = self._embed_texts(texts, show_progress)

        # Save to cache
        if use_cache and self.cache_dir:
            self._save_to_cache(cache_key, embeddings)

        return embeddings

    def embed_queries(
        self,
        queries: list[Query],
        show_progress: bool = False,
    ) -> NDArrayFloat:
        """Generate embeddings for a list of queries.

        Args:
            queries: List of queries to embed.
            show_progress: Whether to show progress bar.

        Returns:
            numpy array of embeddings with shape (num_queries, embedding_dim).
        """
        texts = [query.text for query in queries]
        return self._embed_texts(texts, show_progress)

    def embed_text(self, text: str) -> NDArrayFloat:
        """Generate embedding for a single text.

        Args:
            text: Text to embed.

        Returns:
            numpy array embedding.
        """
        model = self._get_model()
        return model.encode([text], show_progress_bar=False)[0]  # type: ignore[no-any-return]

    def _embed_texts(
        self,
        texts: list[str],
        show_progress: bool = True,
    ) -> NDArrayFloat:
        """Generate embeddings for texts.

        Args:
            texts: List of texts to embed.
            show_progress: Whether to show progress bar.

        Returns:
            numpy array of embeddings.
        """
        model = self._get_model()

        if len(texts) <= self.batch_size:
            # Small batch, embed directly
            return model.encode(texts, show_progress_bar=show_progress)  # type: ignore[no-any-return]

        # Process in batches
        all_embeddings = []
        iterator: Iterable[int] = range(0, len(texts), self.batch_size)

        if show_progress:
            iterator = tqdm(iterator, desc="Generating embeddings")

        for i in iterator:
            batch = texts[i : i + self.batch_size]
            embeddings = model.encode(batch, show_progress_bar=False)
            all_embeddings.append(embeddings)

        return np.vstack(all_embeddings)

    def _get_cache_key(self, chunks: list[Chunk]) -> str:
        """Generate cache key for chunks.

        Args:
            chunks: List of chunks.

        Returns:
            Cache key string.
        """
        # Create a hash of chunk IDs and model name
        content = json.dumps(
            {
                "model": self.model_name,
                "chunk_ids": [c.chunk_id for c in chunks],
            },
            sort_keys=True,
        )
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def _load_from_cache(self, cache_key: str) -> NDArrayFloat | None:
        """Load embeddings from cache.

        Args:
            cache_key: Cache key.

        Returns:
            Cached embeddings or None if not found.
        """
        if not self.cache_dir:
            return None

        cache_path = self.cache_dir / f"{cache_key}.npy"
        if cache_path.exists():
            try:
                return np.load(cache_path, allow_pickle=False)  # type: ignore[no-any-return]
            except Exception:
                return None
        return None

    def _save_to_cache(self, cache_key: str, embeddings: NDArrayFloat) -> None:
        """Save embeddings to cache.

        Args:
            cache_key: Cache key.
            embeddings: Embeddings to cache.
        """
        if not self.cache_dir:
            return

        self.cache_dir.mkdir(parents=True, exist_ok=True)
        cache_path = self.cache_dir / f"{cache_key}.npy"
        with contextlib.suppress(Exception):
            np.save(cache_path, embeddings)

    @property
    def embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by this model."""
        model = self._get_model()
        return model.get_sentence_embedding_dimension()  # type: ignore[no-any-return]
