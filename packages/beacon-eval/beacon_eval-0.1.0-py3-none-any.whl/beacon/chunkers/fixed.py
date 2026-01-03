"""Fixed-size chunking strategy."""

from beacon.chunkers.base import BaseChunker
from beacon.models import Chunk, Document


class FixedSizeChunker(BaseChunker):
    """Chunker that splits text by fixed token/character count."""

    def chunk(self, document: Document) -> list[Chunk]:
        """Split document into fixed-size chunks.

        Args:
            document: The document to chunk.

        Returns:
            List of fixed-size chunks.
        """
        text = document.content
        chunks = []

        # Determine if we're using tokens or characters
        use_tokens = self.params.get("use_tokens", True)

        if use_tokens:
            chunks = self._chunk_by_tokens(text, document.doc_id)
        else:
            chunks = self._chunk_by_characters(text, document.doc_id)

        return chunks

    def _chunk_by_tokens(self, text: str, doc_id: str) -> list[Chunk]:
        """Chunk text by token count."""
        try:
            import tiktoken

            enc = tiktoken.get_encoding("cl100k_base")
            tokens = enc.encode(text)
        except ImportError:
            # Fallback to character-based chunking
            return self._chunk_by_characters(text, doc_id)

        chunks = []
        chunk_index = 0
        start_idx = 0

        while start_idx < len(tokens):
            end_idx = min(start_idx + self.chunk_size, len(tokens))

            # Decode this chunk's tokens back to text
            chunk_tokens = tokens[start_idx:end_idx]
            chunk_text = enc.decode(chunk_tokens)

            # Calculate character positions (approximate)
            if chunk_index == 0:
                start_char = 0
            else:
                # Find the actual position in the original text
                prefix_text = enc.decode(tokens[:start_idx])
                start_char = len(prefix_text)

            end_char = start_char + len(chunk_text)

            chunks.append(
                self._create_chunk(
                    text=chunk_text,
                    doc_id=doc_id,
                    chunk_index=chunk_index,
                    start_char=start_char,
                    end_char=end_char,
                )
            )

            chunk_index += 1
            # Move to next chunk with overlap
            step = max(1, self.chunk_size - self.chunk_overlap)
            start_idx += step

        return chunks

    def _chunk_by_characters(self, text: str, doc_id: str) -> list[Chunk]:
        """Chunk text by character count."""
        chunks = []
        chunk_index = 0
        start_char = 0

        # Convert token-based sizes to character-based (approximate)
        char_chunk_size = self.chunk_size * 4  # ~4 chars per token
        char_overlap = self.chunk_overlap * 4

        while start_char < len(text):
            end_char = min(start_char + char_chunk_size, len(text))

            # Try to break at word boundary
            if end_char < len(text):
                # Look for a space to break at
                space_idx = text.rfind(" ", start_char, end_char)
                if space_idx > start_char + char_chunk_size // 2:
                    end_char = space_idx

            chunk_text = text[start_char:end_char].strip()

            if chunk_text:
                chunks.append(
                    self._create_chunk(
                        text=chunk_text,
                        doc_id=doc_id,
                        chunk_index=chunk_index,
                        start_char=start_char,
                        end_char=end_char,
                    )
                )
                chunk_index += 1

            # Move to next chunk with overlap
            step = max(1, char_chunk_size - char_overlap)
            start_char += step

        return chunks
