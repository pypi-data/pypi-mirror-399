import abc
from abc import ABC, abstractmethod
from gllm_core.schema import Component
from typing import Any

DEPRECATION_MESSAGE: str

class BaseCompressor(Component, ABC, metaclass=abc.ABCMeta):
    """An abstract base class for compressing prompt components in Gen AI applications.

    A prompt may consist of multiple components, such as an instruction, a context, and a query.
    A compressor may be used to compress any number of these components.
    """
    @abstractmethod
    async def compress(self, context: str, query: str, instruction: str | None = None, options: dict[str, Any] | None = None) -> str:
        """Compresses the given context string based on the query and optional instruction.

        This method must be implemented by subclasses to define the specific compression logic.

        Args:
            context (str): The already-packed context string to be compressed.
            query (str): The query related to the context, used for query-dependent compression.
            instruction (str | None, optional): An optional instruction to be considered during compression.
                Defaults to None.
            options (dict[str, Any] | None, optional): Additional options for fine-tuning the compression process.
                The specific supported options depend on the implementing class.
                Defaults to None.

        Returns:
            str: The compressed context string.

        Raises:
            NotImplementedError: This method must be implemented by derived classes.
        """
