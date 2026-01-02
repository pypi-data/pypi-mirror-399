import abc
from abc import ABC
from gllm_misc.multimodal_manager.image_to_text.image_to_text import BaseImageToText as BaseImageToText, IMAGE_DEPRECATION_MESSAGE as IMAGE_DEPRECATION_MESSAGE
from gllm_misc.multimodal_manager.image_to_text.schema.base import ImageToTextResult as ImageToTextResult
from gllm_misc.multimodal_manager.image_to_text.schema.caption import Caption as Caption
from gllm_misc.multimodal_manager.image_to_text.utils import combine_strings as combine_strings, get_image_binary as get_image_binary, get_image_metadata as get_image_metadata, get_unique_non_empty_strings as get_unique_non_empty_strings
from typing import Any

class BaseImageToCaption(BaseImageToText, ABC, metaclass=abc.ABCMeta):
    """Abstract base class for image captioning operations in Gen AI applications.

    This class extends ImageToText to provide specialized functionality for generating
    captions from images. It supports multiple captioning styles and can incorporate additional context
    like oneliner of image, description of image, domain knowledge and metadata.
    """
    def __init__(self) -> None:
        """Initialize the base image to caption component with deprecation warning."""
    async def convert(self, image_source: str | bytes, **kwargs: Any) -> ImageToTextResult:
        '''Convert an image to natural language captions with optional context.

        This method orchestrates the complete image captioning process:
        1. Loads and validates the image from the source
        2. Extracts image metadata (focus on GPS from EXIF data)
        3. Generates captions
        4. Combines the results

        Args:
            image_source (str): Source of the image, which can be:
                1. A file path to a local image
                2. A URL pointing to an image
                3. A base64 encoded image string
                4. An S3 URL for images stored in AWS S3
            **kwargs (Any): Additional keyword arguments including:
                1. number_of_captions (int, optional): Number of captions to generate (default: 5)
                2. image_oneliner (str, optional): Brief one-line summary or title (default: "Not given")
                3. image_description (str, optional): Detailed description of the image (default: "Not given")
                4. domain_knowledge (str, optional): Relevant domain-specific information (default: "Not given")

        Returns:
            ImageToTextResult: A structured result containing:
                1. text: Combined captions as a single string
                2. metadata: A CaptionResult object containing:
                   1. one_liner: Brief one-line summary of the image
                   2. description: Detailed multi-sentence description
                   3. domain_knowledge: Domain-specific context and interpretation
                   4. number_of_captions: Total number of captions generated
                   5. image_metadata: Extracted EXIF and other image metadata

        Raises:
            ValueError: If the image source is invalid or inaccessible
            RuntimeError: If caption generation fails
        '''
