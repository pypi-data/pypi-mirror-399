from _typeshed import Incomplete
from enum import Enum
from gllm_core.schema import Chunk, Component
from gllm_misc.context_manipulator.repacker._strategy import BaseRepackStrategy as BaseRepackStrategy, ForwardRepackStrategy as ForwardRepackStrategy, ReverseRepackStrategy as ReverseRepackStrategy, SidesRepackStrategy as SidesRepackStrategy
from typing import Callable

class RepackMethod(Enum):
    """Enum representing the repack methods."""
    FORWARD = 'forward'
    REVERSE = 'reverse'
    SIDES = 'sides'

class RepackerMode(Enum):
    """Enum representing the repacker modes."""
    CHUNK = 'chunk'
    CONTEXT = 'context'

DEPRECATION_MESSAGE: str

class Repacker(Component):
    """A class for repacking chunks using various strategies.

    Attributes:
        method (RepackMethod): The method used for repacking.
        mode (RepackerMode): The mode of operation (chunk or context).
        delimiter (str): The delimiter used in context mode.
        size_func (Callable[[Chunk], int]): Function used to measure the size of chunks.
        size_limit (int | None): The maximum allowed total size for the repacked chunks.
    """
    method: Incomplete
    mode: Incomplete
    delimiter: Incomplete
    strategy: Incomplete
    size_func: Incomplete
    size_limit: Incomplete
    def __init__(self, method: str = 'forward', mode: str = 'chunk', delimiter: str = '\n\n', size_func: Callable[[Chunk], int] = ..., size_limit: int | None = None) -> None:
        '''Initialize the Repacker instance.

        Args:
            method (str, optional): The method used for repacking. Defaults to "forward".
            mode (str, optional): The mode of operation (chunk or context). Defaults to "chunk".
            delimiter (str, optional): The delimiter used in context mode. Defaults to "\\n\\n".
            size_func (Callable[[Chunk], int], optional): Function used to measure the size of a single chunk.
                Defaults to the length of the chunk content.
            size_limit (int | None, optional): The maximum allowed total size for the repacked chunks. Defaults to None.
                Note: The size limit only accounts for the chunks, not including the delimiter in context mode.
        '''
    async def repack(self, chunks: list[Chunk]) -> list[Chunk] | str:
        """Repack the input chunks based on the chosen method and mode.

        Args:
            chunks (list[Chunk]): The input chunks to repack.

        Returns:
            list[Chunk] | str: The repacked chunks as a list (in chunk mode)
                or a string (in context mode).
        """
