from gllm_inference.lm_invoker import AnthropicLMInvoker
from gllm_inference.output_parser.output_parser import BaseOutputParser as BaseOutputParser
from gllm_inference.prompt_builder import PromptBuilder
from gllm_misc.multimodal_manager.image_to_text.image_to_text_constant import CaptionConstants as CaptionConstants

DEFAULT_SYSTEM_PROMPT: str
DEFAULT_USER_PROMPT: str

def create_default_lm_invoker() -> AnthropicLMInvoker:
    """Create a default language model invoker for lm based image captioning.

    This function initializes and returns an AnthropicLMInvoker instance configured
    for image captioning tasks. It uses the Claude 3.7 Sonnet model which is optimized
    for generating high-quality image captions.

    The function requires the ANTHROPIC_API_KEY environment variable to be set.

    Returns:
        AnthropicLMInvoker: A configured language model invoker instance ready for
            image captioning tasks.

    Raises:
        ValueError: If the ANTHROPIC_API_KEY environment variable is not set.
    """
def create_default_prompt_builder() -> PromptBuilder:
    """Create a default prompt builder with templates for generating image captions.

    This function creates and returns an PromptBuilder instance configured with
    default templates for image captioning tasks. The templates are structured to:

    System prompt:
    - Instructs the model to generate the specified number of captions
    - Specifies output format as a JSON list of captions

    User prompt:
    - Provides structured input format with fields for:
        - Image one-liner
        - Image description
        - Domain knowledge
        - Filename (will be generated from the image given)
        - Image metadata (will be generated from the image given)

    Returns:
        PromptBuilder: A prompt builder instance configured with default
            templates for image captioning.
    """
def get_preset_image_to_caption(preset_name: str) -> tuple[AnthropicLMInvoker, PromptBuilder, BaseOutputParser]:
    """Get the preset configuration for generating image captions.

    Args:
        preset_name (str): The name of the preset to get.

    Returns:
        tuple[AnthropicLMInvoker, PromptBuilder, SafeJSONOutputParser]: A tuple containing the preset
            configuration for image captioning.
    """
