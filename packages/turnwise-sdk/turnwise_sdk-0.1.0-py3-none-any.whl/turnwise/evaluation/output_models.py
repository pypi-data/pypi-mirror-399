"""Output models for evaluation results."""
from typing import Any, Dict, Optional, Type

from pydantic import BaseModel, Field, create_model


class TextOutput(BaseModel):
    """Output model for 'text' type - free-form text evaluation."""

    value: str = Field(description="The evaluation result as text")


class NumberOutput(BaseModel):
    """Output model for 'number' type - numeric evaluation."""

    value: float = Field(description="The numeric evaluation result")


class CheckboxOutput(BaseModel):
    """Output model for 'checkbox' type - boolean evaluation."""

    value: bool = Field(description="True or false evaluation result")


class ScoreOutput(BaseModel):
    """Output model for 'progress' type - score between 0 and 1."""

    score: float = Field(ge=0, le=1, description="Score between 0 and 1")


# Mapping from output type to predefined model
OUTPUT_TYPE_MODELS: Dict[str, Type[BaseModel]] = {
    "text": TextOutput,
    "number": NumberOutput,
    "checkbox": CheckboxOutput,
    "progress": ScoreOutput,
}


def _get_python_type(json_type: str) -> type:
    """Map JSON Schema type to Python type."""
    type_map = {
        "string": str,
        "number": float,
        "integer": int,
        "boolean": bool,
        "array": list,
        "object": dict,
    }
    return type_map.get(json_type, str)


def get_output_model(
    output_schema: Optional[Dict[str, Any]] = None,
    output_type: Optional[str] = None,
) -> Optional[Type[BaseModel]]:
    """
    Get the appropriate Pydantic model for evaluation output.

    Priority:
    1. If output_type is specified and matches a predefined type, use that model
    2. If output_schema is provided, create a dynamic model from the schema
    3. Return None if neither is provided (no structured output)

    Args:
        output_schema: JSON Schema dict (for 'json' type or custom schemas)
        output_type: Output type ('text', 'number', 'checkbox', 'progress', 'json')

    Returns:
        Pydantic model class or None
    """
    # Check for predefined output type first
    if output_type and output_type in OUTPUT_TYPE_MODELS:
        return OUTPUT_TYPE_MODELS[output_type]

    # For 'json' type or if we have a schema, create dynamic model
    if output_schema:
        return create_pydantic_model_from_schema(output_schema)

    return None


def create_pydantic_model_from_schema(
    schema: Dict[str, Any],
    model_name: str = "EvaluationOutput",
) -> Optional[Type[BaseModel]]:
    """
    Create a Pydantic model dynamically from JSON Schema.

    Supports:
    - Object schemas: {"type": "object", "properties": {...}}
    - Primitive schemas: {"type": "number"}, {"type": "string"}, {"type": "boolean"}

    For primitive types, wraps the value in a model with a "value" field.

    Args:
        schema: JSON Schema dict with type, properties, required fields
        model_name: Name for the generated model class

    Returns:
        Pydantic model class or None if schema is invalid
    """
    if not schema:
        return None

    schema_type = schema.get("type")

    # Handle primitive types (number, string, boolean, integer)
    if schema_type in ("number", "string", "boolean", "integer"):
        field_type = _get_python_type(schema_type)
        description = schema.get("description", "")
        return create_model(model_name, value=(field_type, Field(description=description)))

    # Handle object type
    if schema_type != "object":
        return None

    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    if not properties:
        return None

    field_definitions = {}
    for field_name, field_schema in properties.items():
        field_type = _get_python_type(field_schema.get("type", "string"))
        description = field_schema.get("description", "")
        is_required = field_name in required

        if is_required:
            field_definitions[field_name] = (field_type, Field(description=description))
        else:
            field_definitions[field_name] = (
                Optional[field_type],
                Field(default=None, description=description),
            )

    return create_model(model_name, **field_definitions)
