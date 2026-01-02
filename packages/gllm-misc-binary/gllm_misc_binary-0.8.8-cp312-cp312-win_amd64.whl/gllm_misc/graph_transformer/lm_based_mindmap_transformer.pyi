from _typeshed import Incomplete
from gllm_core.schema import Chunk as Chunk
from gllm_inference.lm_invoker.lm_invoker import BaseLMInvoker as BaseLMInvoker
from gllm_inference.prompt_builder import PromptBuilder
from gllm_inference.schema import ModelId as ModelId
from gllm_misc.graph_transformer.constant import MINDMAP_DEFAULT_ALLOWED_NODES as MINDMAP_DEFAULT_ALLOWED_NODES, MINDMAP_DEFAULT_ALLOWED_RELATIONSHIPS as MINDMAP_DEFAULT_ALLOWED_RELATIONSHIPS, MINDMAP_DEFAULT_ROOT_NODE_PROMPT as MINDMAP_DEFAULT_ROOT_NODE_PROMPT, MINDMAP_DEFAULT_ROOT_NODE_TYPE as MINDMAP_DEFAULT_ROOT_NODE_TYPE, MINDMAP_DEFAULT_ROOT_RELATIONSHIP_TYPE as MINDMAP_DEFAULT_ROOT_RELATIONSHIP_TYPE, MINDMAP_DEFAULT_TRANSFORMER_PROMPT as MINDMAP_DEFAULT_TRANSFORMER_PROMPT
from gllm_misc.graph_transformer.lm_based_graph_transformer import LMBasedGraphTransformer as LMBasedGraphTransformer
from gllm_misc.graph_transformer.schema import GraphDocument as GraphDocument, GraphResponse as GraphResponse, Node as Node, Relationship as Relationship
from typing import Any

class LMBasedMindMapTransformer(LMBasedGraphTransformer):
    '''Transform documents into mindmap-based knowledge representations using a language model.

    This class extends LMBasedGraphTransformer to specifically handle the extraction of hierarchical
    mind map structures from text documents. It uses a specialized prompt and default node/relationship
    types designed for mind mapping, organizing content into central themes, main ideas, and sub-ideas.

    The transformer maintains the hierarchical structure of ideas while converting text into a
    graph representation that can be visualized as a mind map.

    The transformer extends LMBasedGraphTransformer by adding specialized functionality for
    merging root nodes and pruning disconnected graph documents to ensure the mind map forms
    a connected graph stemming from a single root node.

    Attributes:
        lm_invoker (BaseLMInvoker): The language model invoker used to generate graph data.
        allowed_nodes (list[str]): List of allowed node types to constrain the output.
            Defaults to MINDMAP_DEFAULT_ALLOWED_NODES (CentralTheme, MainIdea, SubIdea).
        allowed_relationships (list[str] | list[tuple[str, str, str]]): List of allowed
            relationship types to constrain the output. Defaults to MINDMAP_DEFAULT_ALLOWED_RELATIONSHIPS
            which define the hierarchical structure of a mind map.
        root_node_type (str): The type of the root node. Defaults to
            MINDMAP_DEFAULT_ROOT_NODE_TYPE (CentralTheme).
        strict_mode (bool): Whether to strictly enforce node and relationship type constraints.
            Defaults to True.
        use_structured_output (bool): Whether to use the LM\'s structured output capabilities.
            Defaults to True.
        prompt_builder (PromptBuilder, optional): The prompt builder used to generate prompts for the LM.
            If None, creates a default prompt builder with the mind map extraction prompt.

    Example:
        Using an existing LM invoker:

        ```python
        from gllm_inference.lm_invoker import OpenAILMInvoker
        from gllm_misc.graph_transformer import LMBasedMindMapTransformer
        from gllm_core.schema import Chunk

        # Create an LM invoker
        invoker = OpenAILMInvoker(model_name="gpt-4o-mini", api_key="sk-proj-123")

        # Create a mind map transformer
        transformer = LMBasedMindMapTransformer(lm_invoker=invoker)

        # Extract mind map from text
        chunks = [Chunk(content="Artificial Intelligence is transforming industries...")]
        mind_map_docs = await transformer.convert_to_graph_documents(chunks)
        ```

        Building LM invoker from model ID:

        ```python
        from gllm_misc.graph_transformer import LMBasedMindMapTransformer
        from gllm_core.schema import Chunk

        # Create a mind map transformer by specifying model ID
        transformer = LMBasedMindMapTransformer(
            model_id="openai/gpt-4o-mini",
        )

        # Extract mind map from text
        chunks = [Chunk(content="Artificial Intelligence is transforming industries...")]
        mind_map_docs = await transformer.convert_to_graph_documents(chunks)
        ```
    '''
    root_node_type: Incomplete
    def __init__(self, lm_invoker: BaseLMInvoker | None = None, model_id: str | ModelId | None = None, credentials: str | dict[str, Any] | None = None, config: dict[str, Any] | None = None, allowed_nodes: list[str] | None = None, allowed_relationships: list[str] | list[tuple[str, str, str]] | None = None, root_node_type: str | None = None, prompt_builder: PromptBuilder | None = None, strict_mode: bool = True, use_structured_output: bool = True) -> None:
        """Initialize the LMBasedMindMapTransformer with the specified configuration.

        This constructor sets up the mind map transformer with appropriate defaults
        for mind map extraction if not explicitly provided.

        Args:
            lm_invoker (BaseLMInvoker | None, optional): The language model invoker to use for generating graph data.
                Either lm_invoker or model_id must be provided. Defaults to None.
            model_id (str | ModelId | None, optional): The model ID to use for building the LM invoker.
                Required if lm_invoker is not provided. Defaults to None.
            credentials (str | dict[str, Any] | None, optional): Credentials for the LM model.
                Used when building the LM invoker. Defaults to None.
            config (dict[str, Any] | None, optional): Configuration for the LM model.
                Used when building the LM invoker. Defaults to None.
            allowed_nodes (list[str] | None, optional): Optional list of allowed node types. If None,
                defaults to MINDMAP_DEFAULT_ALLOWED_NODES (CentralTheme, MainIdea, SubIdea).
                Defaults to None.
            allowed_relationships (list[str] | list[tuple[str, str, str]] | None, optional): Optional list of
                allowed relationship types. If None, defaults to MINDMAP_DEFAULT_ALLOWED_RELATIONSHIPS
                which define the hierarchical structure of a mind map.
                Defaults to None.
            root_node_type (str | None, optional): Optional root node type. If None,
                uses the default root node type MINDMAP_DEFAULT_ROOT_NODE_TYPE.
                Defaults to None.
            prompt_builder (PromptBuilder | None, optional): Optional prompt builder. If None,
                creates a default prompt builder with the mind map extraction prompt.
                Defaults to None.
            strict_mode (bool, optional): Whether to strictly enforce node and relationship type constraints.
                Defaults to True.
            use_structured_output (bool, optional): Whether to use the LM's structured output capabilities.
                Defaults to True.

        Raises:
            ValueError: If root_node_type is not in allowed_nodes
                or if both/none of lm_invoker and lm_model_id are provided.
        """
    async def convert_to_graph_documents(self, documents: list[Chunk]) -> list[GraphDocument]:
        """Asynchronously convert a sequence of text chunks into graph documents.

        This method overrides the parent class to ensure that each graph document
        has its root nodes merged after processing.

        Args:
            documents (list[Chunk]): A list of Chunk objects containing the text content to
                transform into graphs.

        Returns:
            list[GraphDocument]: A list of GraphDocument objects, each containing nodes and relationships
                extracted from the corresponding input chunk, with merged root nodes.
        """
