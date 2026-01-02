from _typeshed import Incomplete
from enum import Enum
from gllm_core.schema import Chunk as Chunk
from gllm_core.utils import BinaryHandlingStrategy
from gllm_misc.context_manipulator.context_enricher.context_enricher import BaseContextEnricher as BaseContextEnricher, DEPRECATION_MESSAGE as DEPRECATION_MESSAGE

class MetadataPosition(str, Enum):
    """Enum for metadata position options."""
    PREFIX = 'prefix'
    SUFFIX = 'suffix'

class MetadataContextEnricher(BaseContextEnricher):
    """A metadata context enricher that adds metadata to the chunk content.

    This enricher formats metadata fields into a string and appends it to the chunk content
    based on the specified position (prefix or suffix).

    Attributes:
        metadata_fields (list[str]): List of metadata fields to include in the enriched content.
        position (MetadataPosition): Position of the metadata in the content.
            Valid values are defined in the MetadataPosition enum:
            - PREFIX: Metadata block is placed before content
            - SUFFIX: Metadata block is placed after content
        separator (str): Separator between the metadata and the content.
        field_template (str): Template for formatting each metadata field.
        skip_empty (bool): Whether to skip fields with empty values.
        binary_handling (BinaryHandlingStrategy): Strategy for handling binary data.
            Valid values are defined in the BinaryHandlingStrategy:
            - BASE64: Binary data is converted to base64 (default)
            - HEX: Binary data is converted to hexadecimal
            - NONE: Binary data is not included in the metadata block
    """
    metadata_fields: Incomplete
    position: Incomplete
    separator: Incomplete
    field_template: Incomplete
    skip_empty: Incomplete
    binary_handler: Incomplete
    def __init__(self, metadata_fields: list[str], position: MetadataPosition = ..., separator: str = '\n---\n', field_template: str = '- {field}: {value}', skip_empty: bool = True, binary_handling: BinaryHandlingStrategy = ...) -> None:
        '''Initialize the metadata context enricher.

        Args:
            metadata_fields (list[str]): List of metadata field names to include.
            position (MetadataPosition): Where to place metadata block.
                Valid values are defined in the MetadataPosition enum:
                1. "prefix": Metadata block is placed before content
                2. "suffix": Metadata block is placed after content
            separator (str): String to separate metadata from content.
            field_template (str): Template for formatting each metadata field.
                Available fields:
                - {field}: Field name
                - {value}: Field value
            skip_empty (bool): Whether to skip empty fields.
            binary_handling (BinaryHandlingStrategy): Strategy for handling binary data.
                Valid values are defined in the BinaryHandlingStrategy:
                1. "base64": Binary data is converted to base64 (default)
                2. "hex": Binary data is converted to hexadecimal
                3. "none": Binary data is not included in the metadata block
        '''
    async def enrich(self, chunks: list[Chunk]) -> list[Chunk]:
        """Enrich chunks with metadata.

        Args:
            chunks (list[Chunk]): List of chunks to enrich.

        Returns:
            list[Chunk]: List of enriched chunks.
        """
