from _typeshed import Incomplete
from gllm_misc.context_manipulator.compressor.compressor import BaseCompressor as BaseCompressor, DEPRECATION_MESSAGE as DEPRECATION_MESSAGE
from typing import Any

class LLMLinguaCompressor(BaseCompressor):
    """LLMLinguaCompressor is a wrapper for LongLLMLingua's PromptCompressor.

    This class provides a simplified interface for using LongLLMLingua's compression capabilities
    within the GLLM series of libraries, with a focus on the 'longllmlingua' ranking method.
    """
    compressor: Incomplete
    rate: Incomplete
    target_token: Incomplete
    use_sentence_level_filter: Incomplete
    use_context_level_filter: Incomplete
    use_token_level_filter: Incomplete
    rank_method: Incomplete
    def __init__(self, model_name: str = 'NousResearch/Llama-2-7b-hf', device_map: str = 'cuda', rate: float = 0.5, target_token: int = -1, use_sentence_level_filter: bool = False, use_context_level_filter: bool = True, use_token_level_filter: bool = True, rank_method: str = 'longllmlingua') -> None:
        '''Initialize the LLMLinguaCompressor.

        Args:
            model_name (str, optional): The name of the language model to be used.
                Defaults to "NousResearch/Llama-2-7b-hf".
            device_map (str, optional): The device to load the model onto, e.g., "cuda" for GPU.
                Defaults to "cuda".
            rate (float, optional): The default compression rate to be used. Defaults to 0.5.
            target_token (int, optional): The default target token count. Defaults to -1 (no specific target).
            use_sentence_level_filter (bool, optional): Whether to use sentence-level filtering. Defaults to False.
            use_context_level_filter (bool, optional): Whether to use context-level filtering. Defaults to True.
            use_token_level_filter (bool, optional): Whether to use token-level filtering. Defaults to True.
            rank_method (str, optional): The ranking method to use. Recommended is "longllmlingua".
                Defaults to "longllmlingua".
        '''
    async def compress(self, context: str, query: str, instruction: str | None = None, options: dict[str, Any] | None = None) -> str:
        """Compress the given context based on the query and optional instruction.

        Args:
            context (str): The context to be compressed.
            query (str): The query related to the context.
            instruction (str | None, optional): An optional instruction to be considered during compression.
                Defaults to None.
            options (dict[str, Any] | None, optional): Additional options for fine-tuning the compression process.
                Supported keys: rate, target_token, use_sentence_level_filter, use_context_level_filter,
                use_token_level_filter, rank_method.
                Defaults to None.

        Returns:
            str: The compressed context string.

        Raises:
            ValueError: If the compression process fails.
        """
