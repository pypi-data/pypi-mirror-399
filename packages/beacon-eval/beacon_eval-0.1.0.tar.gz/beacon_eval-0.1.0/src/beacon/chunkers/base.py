"""Base chunker class for Beacon."""

from abc import ABC, abstractmethod

from beacon.models import Chunk, ChunkingStrategy, Document


class BaseChunker(ABC):
    """Abstract base class for chunking strategies."""

    def __init__(self, strategy: ChunkingStrategy) -> None:
        """Initialize chunker with strategy configuration."""
        self.strategy = strategy
        self.chunk_size = strategy.chunk_size
        self.chunk_overlap = strategy.chunk_overlap
        self.params = strategy.params

    @abstractmethod
    def chunk(self, document: Document) -> list[Chunk]:
        """Split a document into chunks.

        Args:
            document: The document to chunk.

        Returns:
            List of Chunk objects.
        """
        pass

    def chunk_documents(self, documents: list[Document]) -> list[Chunk]:
        """Chunk multiple documents.

        Args:
            documents: List of documents to chunk.

        Returns:
            List of all chunks from all documents.
        """
        all_chunks = []
        for doc in documents:
            chunks = self.chunk(doc)
            all_chunks.extend(chunks)
        return all_chunks

    def _count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken.

        Falls back to word count approximation if tiktoken fails.
        """
        try:
            import tiktoken

            enc = tiktoken.get_encoding("cl100k_base")
            return len(enc.encode(text))
        except ImportError:
            # Fallback: approximate tokens as words * 1.3
            return int(len(text.split()) * 1.3)

    def _create_chunk(
        self,
        text: str,
        doc_id: str,
        chunk_index: int,
        start_char: int,
        end_char: int,
    ) -> Chunk:
        """Create a Chunk object with metadata."""
        return Chunk(
            text=text,
            doc_id=doc_id,
            chunk_id=f"{doc_id}_chunk_{chunk_index}",
            start_char=start_char,
            end_char=end_char,
            token_count=self._count_tokens(text),
            metadata={
                "strategy": self.strategy.name,
                "chunk_size": self.chunk_size,
                "overlap": self.chunk_overlap,
            },
        )
