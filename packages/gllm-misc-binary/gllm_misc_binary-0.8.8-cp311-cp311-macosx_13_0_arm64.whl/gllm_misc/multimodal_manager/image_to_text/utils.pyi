import aiohttp
from PIL import Image
from _typeshed import Incomplete
from gllm_misc.multimodal_manager.image_to_text.image_to_text_constant import ImageToTextConstants as ImageToTextConstants
from typing import Any

logger: Incomplete

def is_binary_data_image(image_binary_data: bytes) -> bool:
    """Validate if the provided binary data represents a valid image file.

    This function attempts to open the binary data as an image using PIL (Python Imaging Library)
    to verify if it represents a valid image format.

    Args:
        image_binary_data (bytes): The binary data to validate.

    Returns:
        bool: True if the binary data represents a valid image that can be opened by PIL,
            False otherwise.
    """
def get_image_from_base64(image_source: str) -> bytes | None:
    """Decode and validate a base64 encoded image string.

    This function attempts to:
    1. Decode the provided base64 string
    2. Validate that the decoded data represents a valid image
    3. Return the binary data if both steps succeed

    Args:
        image_source (str): The base64 encoded image string to decode.
            Should be a valid base64 string without the data URI prefix
            (e.g., without 'data:image/jpeg;base64,').

    Returns:
        bytes | None: The decoded image binary data if successful and valid,
            None if either the decoding fails or the data is not a valid image.

    Note:
        - The function performs validation using is_binary_data_image()
        - Invalid base64 strings or non-image data will return None
        - Logs debug messages on failure for troubleshooting
    """
def get_image_from_file_path(image_source: str) -> bytes | None:
    """Read image file and return its binary data if valid.

    Args:
        image_source (str): Path to the image file.

    Returns:
        bytes | None: Binary data of the image file if valid, None otherwise.
    """
async def get_image_from_url(image_source: str, timeout: int = 30, session: aiohttp.ClientSession | None = None) -> bytes | None:
    """Asynchronously download and validate an image from a URL.

    This function performs the following steps:
    1. Attempts to download the content from the provided URL
    2. Validates that the downloaded content is a valid image
    3. Returns the binary data if both steps succeed

    Args:
        image_source (str): The URL of the image to download.
            Supports HTTP and HTTPS protocols.
        timeout (int, optional): The timeout for the HTTP request in seconds.
            Defaults to 30 seconds.
        session (Optional[aiohttp.ClientSession], optional): An existing aiohttp session to use.
            If None, a new session will be created. Defaults to None.

    Returns:
        bytes | None: The downloaded image binary data if successful and valid,
            None if the download fails or the content is not a valid image.
    """
def encode_image_to_base64(image: Image.Image, image_format: str = 'PNG') -> str:
    '''Convert PIL Image to base64 string.

    Args:
        image (Image.Image): PIL Image object.
        image_format (str, optional): The format to save the image in.
            Defaults to "PNG".

    Returns:
        str: Base64 encoded image string.
    '''
def get_image_metadata(image_binary: bytes) -> dict[str, Any]:
    """Extract metadata from image binary data.

    This function extracts metadata from the image, including:
    - GPS coordinates (latitude/longitude) if available in EXIF data

    Args:
        image_binary (bytes): The binary data of the image

    Returns:
        dict[str, Any]: Dictionary containing image metadata
    """
def get_image_from_s3(image_source: str) -> bytes | None:
    """Get the image from an S3 URL and return its binary data if valid.

    This function attempts to download image content from an S3 URL and validates that
    the downloaded content is valid image data. It will first try to connect using
    default credentials (instance profile, environment variables, etc), and if that fails,
    it will explicitly check for AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment
    variables. If those fail, it will check for AWS_SESSION_TOKEN.

    Args:
        image_source (str): The S3 URL of the image file (e.g. s3://bucket-name/key or https://bucket-name.s3.region.amazonaws.com/key)

    Returns:
        bytes | None: Binary data of the image file if valid image content is downloaded,
            None if the request fails or content is not valid image.

    Raises:
        ValueError: If no valid AWS credentials are available
    """
async def get_image_binary(image_source: Any) -> tuple[bytes | None, str | None]:
    """Retrieve image binary data from various sources.

    This function acts as a unified interface for retrieving image data from different sources:
    - Local file paths
    - URLs (HTTP/HTTPS)
    - Base64 encoded strings
    - S3 URLs (s3:// or https://)

    The function automatically detects the source type and uses the appropriate method
    to retrieve the image data.

    Args:
        image_source (Any): The source of the image, which can be:
            - bytes: Direct binary data
            - str: Base64 string, file path, URL, or S3 URL

    Returns:
        tuple[bytes | None, str | None]: A tuple containing:
            - The image binary data if successful, None if failed
            - The filename if available, None for direct binary or base64
    """
def get_unique_non_empty_strings(texts: list[str]) -> list[str]:
    """Get unique non-empty strings from a list of strings and remove whitespace.

    This function takes a list of strings and returns a list of strings where each
    string from the list is not empty or whitespace-only. It also removes duplicates.

    Args:
        texts (list[str]): A list of strings to combine.

    Returns:
        list[str]: A list of strings where each string is not empty or whitespace-only.
    """
def combine_strings(texts: list[str]) -> str:
    """Combine multiple strings into a single string with newline separators.

    This function takes a list of strings and returns a single string where each
    string from the list is on a new line. It filters out any empty or whitespace-only
    strings from the list before joining them.

    Args:
        texts (list[str]): A list of strings to combine.

    Returns:
        str: A single string containing all valid strings, where each string is on a new line.
    """
