from _typeshed import Incomplete
from gllm_core.schema import Chunk as Chunk
from gllm_inference.lm_invoker.lm_invoker import BaseLMInvoker as BaseLMInvoker
from gllm_inference.prompt_builder import PromptBuilder as PromptBuilder
from gllm_inference.schema import ModelId as ModelId
from gllm_misc.graph_transformer.schema import GraphDocument as GraphDocument, GraphResponse as GraphResponse, RelationshipTypeFormat as RelationshipTypeFormat
from gllm_misc.graph_transformer.utils import convert_to_graph_document as convert_to_graph_document, create_simple_model as create_simple_model, filter_graph_document_by_allowed_nodes_and_relationships as filter_graph_document_by_allowed_nodes_and_relationships, filter_relationships_by_existing_nodes as filter_relationships_by_existing_nodes, get_default_prompt as get_default_prompt, validate_and_get_relationship_type as validate_and_get_relationship_type
from typing import Any

class LMBasedGraphTransformer:
    '''Transform documents into graph-based documents using a language model.

    This class orchestrates the extraction of knowledge graphs from text documents
    using a language model. It handles prompt construction, model invocation, and
    parsing of results into a standardized graph format.

    The transformer can be configured with constraints on node and relationship types,
    and supports both structured and unstructured output formats from the language model.

    Attributes:
        lm_invoker: The language model invoker used to generate graph data.
        allowed_nodes: List of allowed node types to constrain the output.
        allowed_relationships: List of allowed relationship types to constrain the output.
        strict_mode: Whether to strictly enforce node and relationship type constraints.
        use_structured_output: Whether to use the LM\'s structured output capabilities.
        prompt_builder: The prompt builder used to generate prompts for the LM.

    Example:
        Using an existing LM invoker:

        ```python
        from gllm_inference.lm_invoker import OpenAILMInvoker
        from gllm_misc.graph_transformer import LMBasedGraphTransformer
        from gllm_core.schema import Chunk

        # Create an LM invoker
        invoker = OpenAILMInvoker(model_name="gpt-4o-mini", api_key="sk-proj-123")

        # Create a graph transformer with constraints
        transformer = LMBasedGraphTransformer(
            lm_invoker=invoker,
            allowed_nodes=["Person", "Organization", "Event"],
            allowed_relationships=["WORKS_AT", "PARTICIPATES_IN"]
        )

        # Extract graph from text
        chunks = [Chunk(content="Elon Musk is the CEO of SpaceX and Tesla.")]
        graph_docs = await transformer.convert_to_graph_documents(chunks)
        ```

        Building LM invoker from model ID:

        ```python
        from gllm_misc.graph_transformer import LMBasedGraphTransformer
        from gllm_core.schema import Chunk

        # Create a graph transformer by specifying model ID
        transformer = LMBasedGraphTransformer(
            model_id="openai/gpt-4o-mini",
            allowed_nodes=["Person", "Organization", "Event"],
            allowed_relationships=["WORKS_AT", "PARTICIPATES_IN"]
        )

        # Extract graph from text
        chunks = [Chunk(content="Elon Musk is the CEO of SpaceX and Tesla.")]
        graph_docs = await transformer.convert_to_graph_documents(chunks)
        ```
    '''
    lm_invoker: Incomplete
    def __init__(self, lm_invoker: BaseLMInvoker | None = None, model_id: str | ModelId | None = None, credentials: str | dict[str, Any] | None = None, config: dict[str, Any] | None = None, allowed_nodes: list[str] | None = None, allowed_relationships: list[str] | list[tuple[str, str, str]] | None = None, prompt_builder: PromptBuilder | None = None, strict_mode: bool = True, use_structured_output: bool = False) -> None:
        """Initialize the LMBasedGraphTransformer.

        Args:
            lm_invoker (BaseLMInvoker | None, optional): The language model invoker to use for generating graph data.
                Either lm_invoker or model_id must be provided. Defaults to None.
            model_id (str | ModelId | None, optional): The model ID to use for building the LM invoker.
                Required if lm_invoker is not provided. Defaults to None.
            credentials (str | dict[str, Any] | None, optional): Credentials for the LM model.
                Used when building the LM invoker. Defaults to None.
            config (dict[str, Any] | None, optional): Configuration for the LM model.
                Used when building the LM invoker. Defaults to None.
            allowed_nodes (list[str] | None, optional): Optional list of allowed node types.
                If provided, the transformer will constrain output to only use these node types.
                Defaults to None.
            allowed_relationships (list[str] | list[tuple[str, str, str]] | None, optional): Optional list of allowed
                relationship types. Can be either a list of strings or a list of tuples in the format
                (source_type, relationship_type, target_type).
                Defaults to None.
            prompt_builder (PromptBuilder | None, optional): Optional custom prompt builder. Defaults to a
                prompt builder created using get_default_prompt().
            strict_mode (bool, optional): Determines whether the transformer should apply filtering to
                strictly adhere to allowed_nodes and allowed_relationships.
                Defaults to True.
            use_structured_output (bool, optional): Indicates whether the transformer should use the
                language model's native structured output functionality.
                Defaults to False.
        """
    async def process_response(self, chunk: Chunk) -> GraphDocument:
        """Process a single text chunk and transform it into a graph document.

        This method handles the core transformation logic, including:
        1. Formatting the prompt with the chunk content
        2. Invoking the language model
        3. Parsing the response into nodes and relationships
        4. Applying filtering based on allowed node and relationship types if strict_mode is enabled

        Args:
            chunk (Chunk): A Chunk object containing the text content to transform into a graph

        Returns:
            GraphDocument: A GraphDocument containing the extracted nodes and relationships
        """
    async def convert_to_graph_documents(self, documents: list[Chunk]) -> list[GraphDocument]:
        '''Asynchronously convert a sequence of text chunks into graph documents.

        This method processes multiple chunks in parallel by creating asyncio tasks
        for each document and gathering their results. Each chunk is processed
        independently using the process_response method.

        Args:
            documents (list[Chunk]): A list of Chunk objects containing the text content to
                transform into graphs.

        Returns:
            list[GraphDocument]: A list of GraphDocument objects, each containing nodes and relationships
                extracted from the corresponding input chunk.

        Example:
            ```python
            chunks = [
                Chunk(content="Alice works at Acme Corp."),
                Chunk(content="Bob is the CEO of TechStart.")
            ]
            graph_docs = await transformer.convert_to_graph_documents(chunks)
            # Returns a list of two GraphDocument objects
            ```
        '''
