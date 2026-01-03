"""Recursive character text splitting strategy."""

from typing import Any

from beacon.chunkers.base import BaseChunker
from beacon.models import Chunk, Document


class RecursiveChunker(BaseChunker):
    """Chunker that recursively splits text using multiple separators.

    Similar to LangChain's RecursiveCharacterTextSplitter.
    Tries to split on larger units first (paragraphs, sentences),
    then falls back to smaller units if chunks are still too large.
    """

    # Default separators in order of preference
    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.separators = self.params.get("separators", self.DEFAULT_SEPARATORS)

    def chunk(self, document: Document) -> list[Chunk]:
        """Split document recursively using multiple separators.

        Args:
            document: The document to chunk.

        Returns:
            List of recursively split chunks.
        """
        text = document.content
        chunks_text = self._split_text(text, self.separators)

        # Merge small chunks and handle overlap
        merged_chunks = self._merge_chunks(chunks_text)

        # Create Chunk objects
        chunks = []
        current_pos = 0

        for idx, chunk_text in enumerate(merged_chunks):
            # Find the position in original text
            try:
                start_char = text.index(chunk_text[:50], current_pos)
            except ValueError:
                start_char = current_pos

            end_char = start_char + len(chunk_text)

            chunks.append(
                self._create_chunk(
                    text=chunk_text,
                    doc_id=document.doc_id,
                    chunk_index=idx,
                    start_char=start_char,
                    end_char=end_char,
                )
            )

            # Update position for next search, accounting for overlap
            current_pos = max(current_pos, end_char - self.chunk_overlap * 4)

        return chunks

    def _split_text(self, text: str, separators: list[str]) -> list[str]:
        """Recursively split text using separators.

        Args:
            text: The text to split.
            separators: List of separators to try in order.

        Returns:
            List of text chunks.
        """
        if not text:
            return []

        # Get the first separator that exists in the text
        separator = ""
        for sep in separators:
            if sep == "":
                separator = sep
                break
            if sep in text:
                separator = sep
                break

        # Split the text
        splits = text.split(separator) if separator else list(text)

        # Get remaining separators for recursive splitting
        if separator in separators:
            remaining_separators = separators[separators.index(separator) + 1 :]
        else:
            remaining_separators = []

        # Process each split
        chunks = []
        for split in splits:
            split = split.strip()
            if not split:
                continue

            # If this split is small enough, keep it
            if self._count_tokens(split) <= self.chunk_size:
                chunks.append(split)
            elif remaining_separators:
                # Recursively split further
                sub_chunks = self._split_text(split, remaining_separators)
                chunks.extend(sub_chunks)
            else:
                # Can't split further, just add it
                chunks.append(split)

        return chunks

    def _merge_chunks(self, chunks: list[str]) -> list[str]:
        """Merge small chunks together up to chunk_size.

        Args:
            chunks: List of text chunks.

        Returns:
            List of merged chunks.
        """
        if not chunks:
            return []

        merged = []
        current_chunk = chunks[0]
        current_tokens = self._count_tokens(current_chunk)

        for i in range(1, len(chunks)):
            chunk = chunks[i]
            chunk_tokens = self._count_tokens(chunk)

            # If we can add this chunk without exceeding limit
            if current_tokens + chunk_tokens + 1 <= self.chunk_size:
                current_chunk = current_chunk + " " + chunk
                current_tokens += chunk_tokens + 1
            else:
                # Save current and start new
                merged.append(current_chunk)

                # Handle overlap
                if self.chunk_overlap > 0:
                    # Get the last part of current chunk for overlap
                    overlap_text = self._get_overlap_text(current_chunk)
                    current_chunk = overlap_text + " " + chunk if overlap_text else chunk
                    current_tokens = self._count_tokens(current_chunk)
                else:
                    current_chunk = chunk
                    current_tokens = chunk_tokens

        # Don't forget the last chunk
        if current_chunk:
            merged.append(current_chunk)

        return merged

    def _get_overlap_text(self, text: str) -> str:
        """Get the last portion of text for overlap.

        Args:
            text: The text to get overlap from.

        Returns:
            The overlap portion of text.
        """
        try:
            import tiktoken

            enc = tiktoken.get_encoding("cl100k_base")
            tokens = enc.encode(text)

            if len(tokens) <= self.chunk_overlap:
                return text

            overlap_tokens = tokens[-self.chunk_overlap :]
            return enc.decode(overlap_tokens)
        except Exception:
            # Fallback: use character-based overlap
            char_overlap = self.chunk_overlap * 4
            return text[-char_overlap:] if len(text) > char_overlap else text
