from gllm_inference.prompt_builder import PromptBuilder
from gllm_inference.schema import LMOutput
from gllm_misc.graph_transformer.constant import DEFAULT_NODE_TYPE as DEFAULT_NODE_TYPE, RELATIONSHIP_TUPLE_LENGTH as RELATIONSHIP_TUPLE_LENGTH
from gllm_misc.graph_transformer.schema import GraphDocument as GraphDocument, GraphResponse as GraphResponse, InputType as InputType, Node as Node, PrimitiveNodeType as PrimitiveNodeType, PrimitiveRelationshipType as PrimitiveRelationshipType, Relationship as Relationship, RelationshipTypeFormat as RelationshipTypeFormat, SimpleNode as SimpleNode, SimpleRelationship as SimpleRelationship
from typing import Any

def get_default_prompt(allowed_nodes: list[PrimitiveNodeType] | None = None, allowed_relationships: list[PrimitiveRelationshipType] | None = None, relationship_type: RelationshipTypeFormat | None = None) -> PromptBuilder:
    """Create a prompt for LMBasedGraphTransformer that does not use structured output.

    Args:
        allowed_nodes (list[PrimitiveNodeType] | None, optional): Optional list of allowed node types. Defaults to None.
        allowed_relationships (list[PrimitiveRelationshipType] | None, optional): Optional list of allowed
            relationship types. Defaults to None.
        relationship_type (str | None, optional): Optional string indicating the type of relationship. Defaults to None.

    Returns:
        A PromptBuilder instance with the prompt template.
    """
def optional_enum_field(enum_values: list[str] | list[tuple[str, str, str]] | None = None, description: str = '', input_type: str | InputType = ..., relationship_type: RelationshipTypeFormat | None = None, **field_kwargs: Any) -> Any:
    """Utility function to conditionally create a field with an enum constraint.

    This function creates a Pydantic Field with optional enum constraints based on the
    provided parameters. It handles different LLM types and relationship formats.

    Args:
        enum_values (list[str] | list[tuple[str, str, str]] | None, optional): List of allowed values for the field.
            Can be a list of strings or a list of tuples (relationship_type, source_node, target_node).
            Defaults to None.
        description (str, optional): Description of the field. Defaults to an empty string.
        input_type (InputType, optional): The type of input to get additional information for.
            Defaults to InputType.NODE.
        relationship_type (RelationshipTypeFormat | None, optional): The type of relationship for relationship fields.
            Defaults to None.
        **field_kwargs (Any, optional): Additional keyword arguments to pass to the Field constructor.

    Returns:
        Any: A Pydantic Field with the specified constraints and descriptions.
    """
def create_simple_model(node_labels: list[PrimitiveNodeType] | None = None, rel_types: list[PrimitiveRelationshipType] | None = None, relationship_type: RelationshipTypeFormat | None = None) -> type[GraphResponse]:
    """Create a simple graph model with optional constraints on node and relationship types.

    This public utility function dynamically creates a Pydantic model for graph data
    with optional constraints on node and relationship types. The model includes
    fields for nodes and relationships with appropriate validation rules.

    Args:
        node_labels (list[PrimitiveNodeType] | None, optional): Specifies the allowed node types.
            If None, all node types are allowed. Defaults to None.
        rel_types (list[PrimitiveRelationshipType] | None, optional): Specifies the allowed relationship types.
            Can be either a list of strings or a list of tuples in the format (source_type, relationship_type,
            target_type). If None, all relationship types are allowed. Defaults to None.
        relationship_type (str | None, optional): Type of relationship format. If 'tuple', will extract
            relationship types from the tuples in rel_types. Defaults to None.

    Returns:
        Type[GraphResponse]: A dynamically created Pydantic model class with the specified constraints.

    Raises:
        ValueError: If 'id' is included in the node or relationship properties list.
    """
def map_to_base_node(node: SimpleNode) -> Node:
    """Map the SimpleNode to the base Node.

    This internal helper function converts a dynamically created SimpleNode instance
    to the standard Node class used throughout the application.

    Args:
        node (SimpleNode): A SimpleNode instance from the dynamically created model.

    Returns:
        Node: A standard Node instance with properties copied from the SimpleNode.
    """
def map_to_base_relationship(rel: SimpleRelationship) -> Relationship:
    """Map the SimpleRelationship to the base Relationship.

    This internal helper function converts a dynamically created SimpleRelationship instance
    to the standard Relationship class used throughout the application.

    Args:
        rel (SimpleRelationship): A SimpleRelationship instance from the dynamically created model.

    Returns:
        Relationship: A standard Relationship instance with properties copied from the SimpleRelationship.
    """
def format_property_key(s: str) -> str:
    '''Format property keys in camelCase style.

    This utility function converts a space-separated string into camelCase format,
    which is commonly used for property keys in graph databases and JSON.

    Args:
        s (str): The input string to format as a property key.

    Returns:
        str: The formatted property key in camelCase (first word lowercase,
            subsequent words capitalized with no spaces).

    Examples:
        >>> format_property_key("date of birth")
        \'dateOfBirth\'
        >>> format_property_key("name")
        \'name\'
    '''
def convert_to_graph_document(output: LMOutput | str) -> GraphDocument:
    """Convert LLM output to formatted nodes and relationships.

    This internal helper function processes the output from a language model
    (either as a string or structured LMOutput) and converts it into properly
    formatted lists of nodes and relationships.

    The function handles both structured output (Pydantic model) and unstructured
    output (JSON string) formats, applying appropriate parsing and formatting.

    Args:
        output (LMOutput | str): Either a structured LMOutput object or a JSON string containing
            nodes and relationships data.

    Returns:
        GraphDocument: A GraphDocument containing the extracted nodes and relationships

    Note:
        If parsing fails for string output, empty lists will be returned.
        For structured output, nodes without IDs and relationships without type,
        source_node_id, or target_node_id will be filtered out.
    """
def validate_and_get_relationship_type(allowed_relationships: list[PrimitiveRelationshipType] | None, allowed_nodes: list[PrimitiveNodeType] | None) -> RelationshipTypeFormat | None:
    '''Validate relationship type format and return the format type.

    This utility function validates that the allowed_relationships parameter
    is in one of the expected formats (list of strings or list of tuples)
    and returns the detected format type as an enum.

    Args:
        allowed_relationships (list[PrimitiveRelationshipType] | None, optional): List of allowed relationship types,
            either as:
                - A list of strings (e.g., ["WORKS_AT", "FRIEND_OF"])
                - A list of 3-tuples in the format (source_type, relationship_type, target_type)
                (e.g., [("Person", "WORKS_AT", "Company")])
        allowed_nodes (list[PrimitiveNodeType] | None, optional): Optional list of allowed node types. Required when
            allowed_relationships is a list of tuples to validate that source and
            target node types are in the allowed_nodes list. Defaults to None.

    Returns:
        RelationshipTypeFormat | None: The detected format type:
            - RelationshipTypeFormat.STRING if allowed_relationships is a list of strings
            - RelationshipTypeFormat.TUPLE if allowed_relationships is a list of 3-tuples
            - None if allowed_relationships is empty or None

    Raises:
        ValueError: If allowed_relationships is not a list, or if it contains invalid
            formats, or if tuple source/target types are not in allowed_nodes.
    '''
def filter_relationships_by_existing_nodes(nodes: list[Node], relationships: list[Relationship]) -> list[Relationship]:
    """Remove relationships where source or target node is not in nodes.

    Args:
        nodes (list[Node]): List of nodes.
        relationships (list[Relationship]): List of relationships.

    Returns:
        list[Relationship]: List of relationships where source and target node is in nodes.
    """
def filter_graph_document_by_allowed_nodes_and_relationships(graph_document: GraphDocument, allowed_nodes: list[str] | None, allowed_relationships: list[str] | list[tuple[str, str, str]] | None, relationship_type: RelationshipTypeFormat | None) -> GraphDocument:
    """Filter graph document by allowed nodes and relationships.

    This implementation performs filtering with case-insensitive comparison.

    Args:
        graph_document (GraphDocument): Graph document to filter.
        allowed_nodes (list[str] | None): List of allowed node types.
        allowed_relationships (list[str] | list[tuple[str, str, str]] | None): List of allowed relationship types.
        relationship_type (str | None): Type of relationship.

    Returns:
        GraphDocument: Filtered graph document.
    """
