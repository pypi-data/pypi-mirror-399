"""Faiss-based vector index for similarity search."""

import time
from typing import Any

import numpy as np
import numpy.typing as npt

from beacon.models import Chunk, RetrievalResult

# Type alias for numpy arrays
NDArrayFloat = npt.NDArray[np.floating[Any]]


class FaissIndex:
    """In-memory vector index using Faiss for fast similarity search."""

    def __init__(
        self,
        dimension: int,
        index_type: str = "flat",
        metric: str = "cosine",
    ) -> None:
        """Initialize the Faiss index.

        Args:
            dimension: Dimension of the embeddings.
            index_type: Type of index ('flat', 'ivf', 'hnsw').
            metric: Distance metric ('cosine', 'l2', 'ip').
        """
        self.dimension = dimension
        self.index_type = index_type
        self.metric = metric
        self._index: Any = None
        self._chunks: list[Chunk] = []
        self._id_to_idx: dict[str, int] = {}

    def _create_index(self) -> None:
        """Create the Faiss index."""
        try:
            import faiss
        except ImportError as err:
            raise ImportError(
                "faiss-cpu is required for indexing. "
                "Install with: pip install faiss-cpu"
            ) from err

        if self.index_type == "flat":
            if self.metric == "cosine" or self.metric == "ip":
                # Inner product (cosine similarity for normalized vectors)
                self._index = faiss.IndexFlatIP(self.dimension)
            else:
                # L2 distance
                self._index = faiss.IndexFlatL2(self.dimension)
        elif self.index_type == "ivf":
            # IVF index for larger datasets
            quantizer = faiss.IndexFlatIP(self.dimension)
            nlist = min(100, max(1, len(self._chunks) // 10))
            self._index = faiss.IndexIVFFlat(quantizer, self.dimension, nlist)
        elif self.index_type == "hnsw":
            # HNSW for fast approximate search
            self._index = faiss.IndexHNSWFlat(self.dimension, 32)
        else:
            raise ValueError(f"Unknown index type: {self.index_type}")

    def add(self, chunks: list[Chunk], embeddings: NDArrayFloat) -> None:
        """Add chunks with their embeddings to the index.

        Args:
            chunks: List of chunks.
            embeddings: Numpy array of embeddings (num_chunks, dimension).
        """
        if len(chunks) != len(embeddings):
            raise ValueError(
                f"Number of chunks ({len(chunks)}) must match "
                f"number of embeddings ({len(embeddings)})"
            )

        # Store chunks
        start_idx = len(self._chunks)
        for i, chunk in enumerate(chunks):
            self._id_to_idx[chunk.chunk_id] = start_idx + i
        self._chunks.extend(chunks)

        # Normalize for cosine similarity
        if self.metric == "cosine":
            embeddings = self._normalize(embeddings)

        # Create index if needed
        if self._index is None:
            self._create_index()

        # Add to index
        self._index.add(embeddings.astype(np.float32))

    def search(
        self,
        query_embedding: NDArrayFloat,
        top_k: int = 10,
    ) -> tuple[list[RetrievalResult], float]:
        """Search for similar chunks.

        Args:
            query_embedding: Query embedding vector.
            top_k: Number of results to return.

        Returns:
            Tuple of (list of RetrievalResult, latency in ms).
        """
        if self._index is None or len(self._chunks) == 0:
            return [], 0.0

        # Normalize query for cosine similarity
        if self.metric == "cosine":
            query_embedding = self._normalize(query_embedding.reshape(1, -1))[0]

        # Search
        start_time = time.time()
        scores, indices = self._index.search(
            query_embedding.reshape(1, -1).astype(np.float32),
            min(top_k, len(self._chunks)),
        )
        latency_ms = (time.time() - start_time) * 1000

        # Build results
        results = []
        for rank, (score, idx) in enumerate(zip(scores[0], indices[0], strict=True)):
            if idx < 0:  # Faiss returns -1 for missing results
                continue

            chunk = self._chunks[idx]
            results.append(
                RetrievalResult(
                    chunk_id=chunk.chunk_id,
                    doc_id=chunk.doc_id,
                    score=float(score),
                    text=chunk.text,
                    rank=rank + 1,
                )
            )

        return results, latency_ms

    def batch_search(
        self,
        query_embeddings: NDArrayFloat,
        top_k: int = 10,
    ) -> list[tuple[list[RetrievalResult], float]]:
        """Search for multiple queries at once.

        Args:
            query_embeddings: Array of query embeddings (num_queries, dimension).
            top_k: Number of results per query.

        Returns:
            List of (results, latency) tuples for each query.
        """
        results = []
        for query_emb in query_embeddings:
            results.append(self.search(query_emb, top_k))
        return results

    def _normalize(self, embeddings: NDArrayFloat) -> NDArrayFloat:
        """Normalize embeddings to unit length.

        Args:
            embeddings: Array of embeddings.

        Returns:
            Normalized embeddings.
        """
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1  # Avoid division by zero
        return embeddings / norms  # type: ignore[no-any-return]

    def get_chunk(self, chunk_id: str) -> Chunk | None:
        """Get a chunk by ID.

        Args:
            chunk_id: The chunk ID.

        Returns:
            The chunk or None if not found.
        """
        idx = self._id_to_idx.get(chunk_id)
        if idx is not None:
            return self._chunks[idx]
        return None

    @property
    def num_chunks(self) -> int:
        """Get the number of chunks in the index."""
        return len(self._chunks)

    @property
    def chunks(self) -> list[Chunk]:
        """Get all chunks in the index."""
        return self._chunks
