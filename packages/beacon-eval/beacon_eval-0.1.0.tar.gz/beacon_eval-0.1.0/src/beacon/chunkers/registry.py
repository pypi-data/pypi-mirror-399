"""Registry for chunking strategies."""


from beacon.chunkers.base import BaseChunker
from beacon.chunkers.fixed import FixedSizeChunker
from beacon.chunkers.recursive import RecursiveChunker
from beacon.chunkers.sentence import ParagraphChunker, SentenceChunker
from beacon.models import ChunkingStrategy, ChunkingStrategyType


class ChunkerRegistry:
    """Registry for mapping strategy types to chunker implementations."""

    _chunkers: dict[ChunkingStrategyType, type[BaseChunker]] = {
        ChunkingStrategyType.FIXED_SIZE: FixedSizeChunker,
        ChunkingStrategyType.SENTENCE: SentenceChunker,
        ChunkingStrategyType.PARAGRAPH: ParagraphChunker,
        ChunkingStrategyType.RECURSIVE: RecursiveChunker,
        # Semantic chunker would require embeddings, handled separately
    }

    @classmethod
    def register(
        cls, strategy_type: ChunkingStrategyType, chunker_class: type[BaseChunker]
    ) -> None:
        """Register a chunker class for a strategy type.

        Args:
            strategy_type: The type of chunking strategy.
            chunker_class: The chunker class to use for this strategy.
        """
        cls._chunkers[strategy_type] = chunker_class

    @classmethod
    def get(cls, strategy_type: ChunkingStrategyType) -> type[BaseChunker]:
        """Get the chunker class for a strategy type.

        Args:
            strategy_type: The type of chunking strategy.

        Returns:
            The chunker class.

        Raises:
            ValueError: If no chunker is registered for this strategy type.
        """
        if strategy_type not in cls._chunkers:
            raise ValueError(f"No chunker registered for strategy type: {strategy_type}")
        return cls._chunkers[strategy_type]

    @classmethod
    def list_strategies(cls) -> list[ChunkingStrategyType]:
        """List all registered strategy types.

        Returns:
            List of registered strategy types.
        """
        return list(cls._chunkers.keys())


def get_chunker(strategy: ChunkingStrategy) -> BaseChunker:
    """Get a chunker instance for a strategy.

    Args:
        strategy: The chunking strategy configuration.

    Returns:
        A configured chunker instance.
    """
    # Handle semantic chunking specially (requires embeddings)
    if strategy.strategy_type == ChunkingStrategyType.SEMANTIC:
        from beacon.chunkers.semantic import SemanticChunker

        return SemanticChunker(strategy)

    chunker_class = ChunkerRegistry.get(strategy.strategy_type)
    return chunker_class(strategy)
