"""Semantic chunking strategy using embeddings."""

from typing import Any

import numpy as np
import numpy.typing as npt

from beacon.chunkers.base import BaseChunker
from beacon.models import Chunk, Document

# Type alias for numpy arrays
NDArrayFloat = npt.NDArray[np.floating[Any]]


class SemanticChunker(BaseChunker):
    """Chunker that splits text at semantic boundaries using embeddings.

    Uses cosine similarity between adjacent sentences to detect
    topic shifts and create chunks at natural boundaries.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.embedding_model = self.params.get("embedding_model", "all-MiniLM-L6-v2")
        self.breakpoint_threshold = self.params.get("breakpoint_threshold", 0.5)
        self._model: Any = None

    def _get_model(self) -> Any:
        """Lazy load the embedding model."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer

                self._model = SentenceTransformer(self.embedding_model)
            except ImportError as err:
                raise ImportError(
                    "sentence-transformers is required for semantic chunking. "
                    "Install with: pip install sentence-transformers"
                ) from err
        return self._model

    def chunk(self, document: Document) -> list[Chunk]:
        """Split document at semantic boundaries.

        Args:
            document: The document to chunk.

        Returns:
            List of semantically coherent chunks.
        """
        text = document.content
        sentences = self._split_into_sentences(text)

        if len(sentences) <= 1:
            # Not enough sentences to find breakpoints
            return [
                self._create_chunk(
                    text=text,
                    doc_id=document.doc_id,
                    chunk_index=0,
                    start_char=0,
                    end_char=len(text),
                )
            ]

        # Get embeddings for all sentences
        model = self._get_model()
        embeddings = model.encode(sentences, show_progress_bar=False)

        # Find breakpoints based on similarity
        breakpoints = self._find_breakpoints(embeddings)

        # Create chunks from breakpoints
        chunks = self._create_chunks_from_breakpoints(
            sentences, breakpoints, document.doc_id, text
        )

        return chunks

    def _split_into_sentences(self, text: str) -> list[str]:
        """Split text into sentences for embedding.

        Args:
            text: The text to split.

        Returns:
            List of sentences.
        """
        import re

        # Simple sentence splitting
        sentence_endings = re.compile(r"(?<=[.!?])\s+")
        sentences = sentence_endings.split(text)

        # Clean up
        cleaned = []
        for s in sentences:
            s = s.strip()
            if s:
                cleaned.append(s)

        return cleaned

    def _find_breakpoints(self, embeddings: NDArrayFloat) -> list[int]:
        """Find semantic breakpoints based on embedding similarity.

        Args:
            embeddings: Array of sentence embeddings.

        Returns:
            List of indices where chunks should be split.
        """
        # Calculate cosine similarity between adjacent sentences
        similarities = []
        for i in range(len(embeddings) - 1):
            sim = self._cosine_similarity(embeddings[i], embeddings[i + 1])
            similarities.append(sim)

        if not similarities:
            return []

        # Find breakpoints where similarity drops significantly
        # Use percentile-based threshold
        threshold = np.percentile(similarities, self.breakpoint_threshold * 100)

        breakpoints = []
        current_chunk_size = 0

        for i, sim in enumerate(similarities):
            current_chunk_size += 1

            # Check if we should break here
            should_break = False

            # Break if similarity is below threshold
            if sim < threshold:
                should_break = True

            # Also break if chunk is getting too large
            if current_chunk_size >= self.chunk_size // 50:  # Approximate sentences per chunk
                should_break = True

            if should_break:
                breakpoints.append(i + 1)
                current_chunk_size = 0

        return breakpoints

    def _cosine_similarity(self, a: NDArrayFloat, b: NDArrayFloat) -> float:
        """Calculate cosine similarity between two vectors.

        Args:
            a: First vector.
            b: Second vector.

        Returns:
            Cosine similarity score.
        """
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return float(dot_product / (norm_a * norm_b))

    def _create_chunks_from_breakpoints(
        self,
        sentences: list[str],
        breakpoints: list[int],
        doc_id: str,
        original_text: str,
    ) -> list[Chunk]:
        """Create chunks from sentences and breakpoints.

        Args:
            sentences: List of sentences.
            breakpoints: List of breakpoint indices.
            doc_id: Document ID.
            original_text: Original document text.

        Returns:
            List of chunks.
        """
        chunks = []
        chunk_index = 0
        start_idx = 0

        # Add end of document as final breakpoint
        all_breakpoints = breakpoints + [len(sentences)]

        for end_idx in all_breakpoints:
            if start_idx >= end_idx:
                continue

            chunk_sentences = sentences[start_idx:end_idx]
            chunk_text = " ".join(chunk_sentences)

            # Find position in original text
            try:
                start_char = original_text.find(chunk_sentences[0][:30])
                if start_char == -1:
                    start_char = 0
            except Exception:
                start_char = 0

            end_char = start_char + len(chunk_text)

            chunks.append(
                self._create_chunk(
                    text=chunk_text,
                    doc_id=doc_id,
                    chunk_index=chunk_index,
                    start_char=start_char,
                    end_char=min(end_char, len(original_text)),
                )
            )

            chunk_index += 1
            start_idx = end_idx

        return chunks
