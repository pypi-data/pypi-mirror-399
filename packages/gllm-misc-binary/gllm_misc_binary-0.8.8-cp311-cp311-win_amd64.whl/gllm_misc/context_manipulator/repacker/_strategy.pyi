import abc
from abc import ABC, abstractmethod
from typing import TypeVar

T = TypeVar('T')

class BaseRepackStrategy(ABC, metaclass=abc.ABCMeta):
    """Abstract base class for repacking strategies.

    This class defines the interface that all repacking strategies must implement.
    """
    @abstractmethod
    def repack(self, chunks: list[T]) -> list[T]:
        """Repack the given chunks.

        Args:
            chunks (list[T]): The chunks to be repacked.

        Returns:
            list[T]: The repacked chunks.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """

class ForwardRepackStrategy(BaseRepackStrategy):
    """Repacking strategy that returns chunks in their original order."""
    def repack(self, chunks: list[T]) -> list[T]:
        """Return the chunks in their original order.

        Args:
            chunks (list[T]): The chunks to be repacked.

        Returns:
            list[T]: The chunks in their original order.
        """

class ReverseRepackStrategy(BaseRepackStrategy):
    """Repacking strategy that returns chunks in reverse order."""
    def repack(self, chunks: list[T]) -> list[T]:
        """Return the chunks in reverse order.

        Args:
            chunks (list[T]): The chunks to be repacked.

        Returns:
            list[T]: The chunks in reverse order.
        """

class SidesRepackStrategy(BaseRepackStrategy):
    """Repacking strategy that alternates chunks from the end and start."""
    def repack(self, chunks: list[T]) -> list[T]:
        """Return the chunks in an alternating order from the end and start.

        This ordering places the most relevant chunks at the beginning and end of the list. This is useful when
        dealing with particularly long contexts, where the model might suffer from the lost-in-the-middle problem.

        This implementation is taken from LangChain [1]. We reimplement them here since LangChain requires a list of
        `Document` objects, which we might replace in the future.

        Args:
            chunks (list[T]): The chunks to be repacked.

        Returns:
            list[T]: The chunks in an alternating order.
        """
