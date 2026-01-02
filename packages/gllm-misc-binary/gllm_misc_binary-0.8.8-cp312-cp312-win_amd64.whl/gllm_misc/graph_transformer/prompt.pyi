from gllm_misc.graph_transformer.schema import PrimitiveNodeType as PrimitiveNodeType, PrimitiveRelationshipType as PrimitiveRelationshipType

def get_default_graph_transformer_system_prompt(allowed_nodes: list[PrimitiveNodeType] | None = None, allowed_relationships: list[PrimitiveRelationshipType] | None = None) -> str:
    """Generate system prompt with optional allowed nodes and relationships.

    This is a public utility function that creates a formatted system prompt for LLMs
    to guide knowledge graph extraction. The prompt includes instructions for the model
    on how to identify and structure entities and relationships.

    Args:
        allowed_nodes (list[PrimitiveNodeType] | None, optional): Optional list of allowed node types.
            If provided, the prompt will instruct the model to only use these specific node types. Defaults to None.
        allowed_relationships (list[PrimitiveRelationshipType] | None, optional): Optional list of allowed
            relationship types. If provided, the prompt will instruct the model to only use these specific
            relationship types. Defaults to None.

    Returns:
        str: Formatted system prompt string ready to be used with an LLM.
    """
