from _typeshed import Incomplete
from gllm_core.schema import Chunk as Chunk
from gllm_inference.em_invoker.em_invoker import BaseEMInvoker as BaseEMInvoker
from gllm_misc.context_manipulator.relevance_filter.relevance_filter import BaseRelevanceFilter as BaseRelevanceFilter, DEPRECATION_MESSAGE as DEPRECATION_MESSAGE

class SimilarityBasedRelevanceFilter(BaseRelevanceFilter):
    """Relevance filter that uses semantic similarity to determine chunk relevance.

    Attributes:
        em_invoker (BaseEMInvoker): The embedding model invoker to use for vectorization.
        threshold (float): The similarity threshold for relevance (0 to 1). Defaults to 0.5.
    """
    em_invoker: Incomplete
    threshold: Incomplete
    def __init__(self, em_invoker: BaseEMInvoker, threshold: float = 0.5) -> None:
        """Initialize the SimilarityBasedRelevanceFilter.

        Args:
            em_invoker (BaseEMInvoker): The embedding model invoker to use for vectorization.
            threshold (float, optional): The similarity threshold for relevance (0 to 1). Defaults to 0.5.

        Raises:
            ValueError: If the threshold is not between 0 and 1.
        """
    async def filter(self, chunks: list[Chunk], query: str) -> list[Chunk]:
        """Filter the given chunks based on their semantic similarity to the query.

        This method calculates the similarity between the query and each text chunk.
        For now, non-text chunks are excluded from processing and similarity calculation.

        Args:
            chunks (list[Chunk]): The list of chunks to filter.
            query (str): The query to compare chunks against.

        Returns:
            list[Chunk]: A list of relevant text chunks. Non-text chunks are not included in the result.
        """
