import abc
from abc import ABC, abstractmethod
from gllm_core.schema import Chunk, Component

DEPRECATION_MESSAGE: str

class BaseContextEnricher(Component, ABC, metaclass=abc.ABCMeta):
    """An abstract base class for the context enrichers used in Gen AI applications.

    This class extends the Component base class to provide context enrichment
    functionality for chunks of text or binary data. Subclasses must implement
    the enrich method to define specific enrichment behavior.
    """
    @abstractmethod
    async def enrich(self, chunks: list[Chunk]) -> list[Chunk]:
        """Enrich a list of chunks with additional context.

        This abstract method must be implemented by subclasses to define
        their specific enrichment behavior.

        Args:
            chunks (list[Chunk]): List of Chunk objects to enrich. Must not be None.

        Returns:
            list[Chunk]: List of enriched Chunk objects.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
