"""
Schema-Constrained Tool Call Validator for Sovereign Agentic Core.
Enforces strict parameter schemas and data types on model-generated tool arguments.
"""

from typing import Dict, Any, Optional, Tuple, Type, get_type_hints
from pydantic import BaseModel, ValidationError, create_model, Field
import inspect


class SchemaValidationResult(BaseModel):
    is_valid: bool
    validated_args: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None
    remediation_hint: Optional[str] = None


class SchemaValidator:
    """
    Validates model-generated tool arguments against tool schemas or Python type hints.
    Provides structured repair guidance if validation fails.
    """

    def __init__(self):
        self._tool_models: Dict[str, Type[BaseModel]] = {}

    def register_tool_schema(self, tool_name: str, pydantic_model: Type[BaseModel]):
        """Explicitly registers a Pydantic model schema for a tool."""
        self._tool_models[tool_name] = pydantic_model

    def derive_schema_from_callable(self, tool_name: str, func: Any):
        """Dynamically derives a Pydantic validation schema from a Python callable's signatures."""
        sig = inspect.signature(func)
        fields = {}
        for param_name, param in sig.parameters.items():
            if param_name in ("self", "cls"):
                continue
            annotation = param.annotation if param.annotation != inspect.Parameter.empty else Any
            default = param.default if param.default != inspect.Parameter.empty else ...
            fields[param_name] = (annotation, default)

        dynamic_model = create_model(f"{tool_name}_Schema", **fields)
        self._tool_models[tool_name] = dynamic_model

    def validate(self, tool_name: str, raw_args: Dict[str, Any]) -> SchemaValidationResult:
        """Validates tool arguments against the registered schema."""
        if tool_name not in self._tool_models:
            # If no strict model is registered, allow through
            return SchemaValidationResult(is_valid=True, validated_args=raw_args)

        model_cls = self._tool_models[tool_name]
        try:
            instance = model_cls(**raw_args)
            return SchemaValidationResult(
                is_valid=True,
                validated_args=instance.model_dump()
            )
        except ValidationError as ve:
            errors = ve.errors()
            err_details = []
            remediation = []
            for e in errors:
                loc = " -> ".join([str(l) for l in e["loc"]])
                msg = e["msg"]
                err_details.append(f"Field '{loc}': {msg}")
                remediation.append(f"Please provide '{loc}' with expected format ({e.get('type')}).")

            return SchemaValidationResult(
                is_valid=False,
                validated_args=raw_args,
                error_message="; ".join(err_details),
                remediation_hint=" | ".join(remediation)
            )
