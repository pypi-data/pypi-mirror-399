import abc
from abc import ABC, abstractmethod
from gllm_core.schema import Component
from gllm_misc.multimodal_manager.image_to_text.schema.base import ImageToTextResult as ImageToTextResult

IMAGE_DEPRECATION_MESSAGE: str

class BaseImageToText(Component, ABC, metaclass=abc.ABCMeta):
    """An abstract base class for image to text conversion used in Gen AI applications.

    This class provides a foundation for building image to text converter components in Gen AI applications.
    It supports various types of image sources (file paths, URLs, base64 strings) and can be extended
    to implement different types of image analysis tasks like OCR, captioning, or object detection.
    """
    def __init__(self) -> None:
        """Initialize the base image to text component with logging capabilities."""
    @abstractmethod
    async def convert(self, image_source: str | bytes, **kwargs) -> ImageToTextResult:
        """Process the image and convert it to text.

        This abstract method must be implemented by subclasses to define how the image is converted to text.
        It supports various image sources and can be customized for different types of text extraction tasks.

        Args:
            image_source (str | bytes): Source of the image, which can be:
                1. A file path to a local image
                2. A URL pointing to an image
                3. A base64 encoded image string
                4. An S3 URL (s3:// or https://) for images stored in AWS S3
            **kwargs: Additional configuration parameters specific to each implementation.
                These parameters allow customization of the conversion process.

        Returns:
            ImageToTextResult: The result of processing the image, containing:
                1. Extracted text or generated captions
                2. Metadata about the image
                3. Additional processing information

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
