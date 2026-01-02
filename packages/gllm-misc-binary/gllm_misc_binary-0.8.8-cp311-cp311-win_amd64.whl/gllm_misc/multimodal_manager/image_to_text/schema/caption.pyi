from gllm_misc.multimodal_manager.image_to_text.image_to_text_constant import CaptionConstants as CaptionConstants, ImageToTextConstants as ImageToTextConstants
from pydantic import BaseModel
from typing import Any

class Caption(BaseModel):
    """Result class for image captioning operations.

    This class extends ImageToTextResult to provide a structured format
    for image captioning results, supporting:
    - Multiple caption types (one-liner, detailed, domain-specific)
    - Caption count tracking
    - Metadata storage for processing details

    Attributes:
        image_one_liner (str): Brief, single-sentence summary of the image.
            Defaults to empty string if not provided.
        image_description (str): Detailed, multi-sentence description of the image.
            Defaults to empty string if not provided.
        domain_knowledge (str): Domain-specific interpretation or context.
            Defaults to empty string if not provided.
        number_of_captions (int): Total number of distinct captions generated.
            Defaults to 0 if no captions are generated.
        image_metadata (dict[str, Any]): Additional information about the captioning process:
            - Model configuration
            - Processing parameters
            - Confidence scores
            - Timing information
            - Error messages (if any)
    """
    image_one_liner: str
    image_description: str
    domain_knowledge: str
    number_of_captions: int
    image_metadata: dict[str, Any]
    def handle_none_values(str_value: Any) -> Any:
        """Handle None values by converting them to default values."""
    def handle_none_number_of_captions(caption_value: Any) -> Any:
        """Handle None values for number_of_captions by using default."""
    def handle_none_metadata(metadata_value: Any) -> Any:
        """Handle None values for image_metadata by using empty dict."""
