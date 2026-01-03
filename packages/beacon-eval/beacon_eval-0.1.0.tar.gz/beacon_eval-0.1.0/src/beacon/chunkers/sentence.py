"""Sentence-based chunking strategy."""

import re

from beacon.chunkers.base import BaseChunker
from beacon.models import Chunk, Document


class SentenceChunker(BaseChunker):
    """Chunker that splits text by sentence boundaries."""

    # Sentence-ending punctuation patterns
    SENTENCE_ENDINGS = re.compile(r"(?<=[.!?])\s+(?=[A-Z])")

    # More aggressive sentence splitting for edge cases
    SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")

    def chunk(self, document: Document) -> list[Chunk]:
        """Split document into sentence-based chunks.

        Groups sentences together until chunk_size is reached.

        Args:
            document: The document to chunk.

        Returns:
            List of sentence-based chunks.
        """
        text = document.content
        sentences = self._split_sentences(text)

        chunks = []
        chunk_index = 0
        current_sentences: list[str] = []
        current_tokens = 0
        current_start = 0

        for sentence in sentences:
            sentence_tokens = self._count_tokens(sentence)

            # If adding this sentence exceeds chunk_size, save current chunk
            if current_tokens + sentence_tokens > self.chunk_size and current_sentences:
                chunk_text = " ".join(current_sentences)
                end_char = current_start + len(chunk_text)

                chunks.append(
                    self._create_chunk(
                        text=chunk_text,
                        doc_id=document.doc_id,
                        chunk_index=chunk_index,
                        start_char=current_start,
                        end_char=end_char,
                    )
                )
                chunk_index += 1

                # Handle overlap: keep last few sentences
                if self.chunk_overlap > 0:
                    overlap_sentences: list[str] = []
                    overlap_tokens = 0
                    for s in reversed(current_sentences):
                        s_tokens = self._count_tokens(s)
                        if overlap_tokens + s_tokens <= self.chunk_overlap:
                            overlap_sentences.insert(0, s)
                            overlap_tokens += s_tokens
                        else:
                            break
                    current_sentences = overlap_sentences
                    current_tokens = overlap_tokens
                    # Update start position for overlap
                    if overlap_sentences:
                        overlap_text = " ".join(overlap_sentences)
                        current_start = end_char - len(overlap_text)
                else:
                    current_sentences = []
                    current_tokens = 0
                    current_start = end_char + 1

            current_sentences.append(sentence)
            current_tokens += sentence_tokens

        # Don't forget the last chunk
        if current_sentences:
            chunk_text = " ".join(current_sentences)
            end_char = current_start + len(chunk_text)

            chunks.append(
                self._create_chunk(
                    text=chunk_text,
                    doc_id=document.doc_id,
                    chunk_index=chunk_index,
                    start_char=current_start,
                    end_char=min(end_char, len(text)),
                )
            )

        return chunks

    def _split_sentences(self, text: str) -> list[str]:
        """Split text into sentences.

        Uses regex-based sentence detection.

        Args:
            text: The text to split.

        Returns:
            List of sentences.
        """
        # First, try the stricter pattern
        sentences = self.SENTENCE_ENDINGS.split(text)

        # If we got very few splits, try the more aggressive pattern
        if len(sentences) <= 2 and len(text) > 500:
            sentences = self.SENTENCE_SPLIT.split(text)

        # Clean up sentences
        cleaned = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                cleaned.append(sentence)

        return cleaned


class ParagraphChunker(BaseChunker):
    """Chunker that splits text by paragraph boundaries."""

    def chunk(self, document: Document) -> list[Chunk]:
        """Split document into paragraph-based chunks.

        Groups paragraphs together until chunk_size is reached.

        Args:
            document: The document to chunk.

        Returns:
            List of paragraph-based chunks.
        """
        text = document.content
        paragraphs = self._split_paragraphs(text)

        chunks = []
        chunk_index = 0
        current_paragraphs: list[str] = []
        current_tokens = 0
        current_start = 0

        for paragraph in paragraphs:
            para_tokens = self._count_tokens(paragraph)

            # If a single paragraph exceeds chunk_size, it becomes its own chunk
            if para_tokens > self.chunk_size:
                # Save current chunk if any
                if current_paragraphs:
                    chunk_text = "\n\n".join(current_paragraphs)
                    end_char = current_start + len(chunk_text)

                    chunks.append(
                        self._create_chunk(
                            text=chunk_text,
                            doc_id=document.doc_id,
                            chunk_index=chunk_index,
                            start_char=current_start,
                            end_char=end_char,
                        )
                    )
                    chunk_index += 1
                    current_start = end_char + 2  # +2 for \n\n

                # Add the large paragraph as its own chunk
                end_char = current_start + len(paragraph)
                chunks.append(
                    self._create_chunk(
                        text=paragraph,
                        doc_id=document.doc_id,
                        chunk_index=chunk_index,
                        start_char=current_start,
                        end_char=end_char,
                    )
                )
                chunk_index += 1
                current_start = end_char + 2
                current_paragraphs = []
                current_tokens = 0
                continue

            # If adding this paragraph exceeds chunk_size, save current chunk
            if current_tokens + para_tokens > self.chunk_size and current_paragraphs:
                chunk_text = "\n\n".join(current_paragraphs)
                end_char = current_start + len(chunk_text)

                chunks.append(
                    self._create_chunk(
                        text=chunk_text,
                        doc_id=document.doc_id,
                        chunk_index=chunk_index,
                        start_char=current_start,
                        end_char=end_char,
                    )
                )
                chunk_index += 1
                current_start = end_char + 2
                current_paragraphs = []
                current_tokens = 0

            current_paragraphs.append(paragraph)
            current_tokens += para_tokens

        # Don't forget the last chunk
        if current_paragraphs:
            chunk_text = "\n\n".join(current_paragraphs)
            end_char = current_start + len(chunk_text)

            chunks.append(
                self._create_chunk(
                    text=chunk_text,
                    doc_id=document.doc_id,
                    chunk_index=chunk_index,
                    start_char=current_start,
                    end_char=min(end_char, len(text)),
                )
            )

        return chunks

    def _split_paragraphs(self, text: str) -> list[str]:
        """Split text into paragraphs.

        Args:
            text: The text to split.

        Returns:
            List of paragraphs.
        """
        # Split on double newlines
        paragraphs = re.split(r"\n\s*\n", text)

        # Clean up paragraphs
        cleaned = []
        for para in paragraphs:
            para = para.strip()
            if para:
                cleaned.append(para)

        return cleaned
