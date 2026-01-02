import abc
from abc import ABC, abstractmethod
from gllm_core.schema import Chunk, Component

DEPRECATION_MESSAGE: str

class BaseRelevanceFilter(Component, ABC, metaclass=abc.ABCMeta):
    """Abstract base class for relevance filters."""
    @abstractmethod
    async def filter(self, chunks: list[Chunk], query: str) -> list[Chunk]:
        """Filter the given chunks based on their relevance to the query.

        Args:
            chunks (list[Chunk]): The list of chunks to filter.
            query (str): The query to compare chunks against.

        Returns:
            list[Chunk]: A list of relevant chunks.

        Raises:
            NotImplementedError: If the filter method is not implemented by the subclass.
        """
