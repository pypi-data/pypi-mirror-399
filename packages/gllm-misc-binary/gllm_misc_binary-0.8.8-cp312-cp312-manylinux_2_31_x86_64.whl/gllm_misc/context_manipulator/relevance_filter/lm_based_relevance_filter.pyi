from _typeshed import Incomplete
from gllm_core.schema import Chunk as Chunk
from gllm_inference.request_processor import LMRequestProcessor as LMRequestProcessor, UsesLM
from gllm_misc.context_manipulator.relevance_filter.relevance_filter import BaseRelevanceFilter as BaseRelevanceFilter, DEPRECATION_MESSAGE as DEPRECATION_MESSAGE
from typing import Callable

DEFAULT_BATCH_SIZE: int
DEFAULT_CHUNK_TEMPLATE: str

class LMBasedRelevanceFilter(BaseRelevanceFilter, UsesLM):
    '''Relevance filter that uses an LM to determine chunk relevance.

    This filter processes chunks in batches, sending them to an LM for relevance determination.
    It handles potential LM processing failures with a simple strategy controlled by the
    \'on_failure_keep_all\' parameter.

    The LM is expected to return a specific output format for each chunk, indicating its
    relevance to the given query.

    The expected LM output format is:
    ```
        {
            "results": [
                {
                    "explanation": str,
                    "is_relevant": bool
                },
                ...
            ]
        }
    ```

    The number of items in "results" should match the number of input chunks.

    Attributes:
        lm_request_processor (LMRequestProcessor): The LM request processor used for LM calls.
        batch_size (int): The number of chunks to process in each LM call.
        on_failure_keep_all (bool): If True, keep all chunks when LM processing fails.
            If False, discard all chunks from the failed batch.
        metadata (list[str] | None): List of metadata fields to include.
            If None, no metadata is included.
        chunk_format (str | Callable[[Chunk], str]): Either a format string
            or a callable for custom chunk formatting. If using a format string:
            - Use {content} for chunk content
            - Use {metadata} for auto-formatted metadata block
            - Or reference metadata fields directly: {field_name}
    '''
    lm_request_processor: Incomplete
    batch_size: Incomplete
    on_failure_keep_all: Incomplete
    metadata: Incomplete
    chunk_format: Incomplete
    def __init__(self, lm_request_processor: LMRequestProcessor, batch_size: int = ..., on_failure_keep_all: bool = True, metadata: list[str] | None = None, chunk_format: str | Callable[[Chunk], str] = ...) -> None:
        """Initialize the LMBasedRelevanceFilter.

        Args:
            lm_request_processor (LMRequestProcessor): The LM request processor to use for LM calls.
            batch_size (int, optional): The number of chunks to process in each LM call.
                Defaults to DEFAULT_BATCH_SIZE.
            on_failure_keep_all (bool, optional): If True, keep all chunks when LM processing fails.
                If False, discard all chunks from the failed batch. Defaults to True.
            metadata (list[str] | None, optional): List of metadata fields to include.
                If None, no metadata is included.
            chunk_format (str | Callable[[Chunk], str], optional): Either a format string
                or a callable for custom chunk formatting. If using a format string:
                - Use {content} for chunk content
                - Use {metadata} for auto-formatted metadata block
                - Or reference metadata fields directly: {field_name}
                Defaults to DEFAULT_CHUNK_TEMPLATE.
        """
    async def filter(self, chunks: list[Chunk], query: str) -> list[Chunk]:
        """Filter the given chunks based on their relevance to the query using an LM.

        This method processes chunks in batches, sending each batch to the LM for relevance
        determination. If LM processing fails for a batch, the behavior is determined by
        the 'on_failure_keep_all' attribute.

        Args:
            chunks (list[Chunk]): The list of chunks to filter.
            query (str): The query to compare chunks against.

        Returns:
            list[Chunk]: A list of chunks deemed relevant by the LM.
        """
