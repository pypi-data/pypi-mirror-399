"""Decorators for keyword registration and parameter definition."""

import functools
import inspect
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Type, Union

from .registry import keyword_registry


class ParamDirection(Enum):
    """Parameter direction enumeration."""

    INPUT = "input"
    OUTPUT = "output"


class ParamType(Enum):
    """Parameter type enumeration."""

    STRING = "string"
    NUMBER = "number"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    OBJECT = "object"
    ARRAY = "array"
    ANY = "any"


@dataclass
class ParamDefinition:
    """Definition of a keyword parameter."""

    name: str
    direction: ParamDirection = ParamDirection.INPUT
    type: Union[ParamType, str] = ParamType.STRING
    required: bool = False
    default: Any = None
    description: str = ""
    choices: Optional[List[Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "name": self.name,
            "direction": (
                self.direction.value
                if isinstance(self.direction, ParamDirection)
                else self.direction
            ),
            "type": self.type.value if isinstance(self.type, ParamType) else self.type,
            "required": self.required,
            "description": self.description,
        }
        if self.default is not None:
            result["default"] = self.default
        if self.choices is not None:
            result["choices"] = self.choices
        return result


# Type mapping from Python types to ParamType
_PYTHON_TYPE_MAP: Dict[Type, ParamType] = {
    str: ParamType.STRING,
    int: ParamType.INTEGER,
    float: ParamType.NUMBER,
    bool: ParamType.BOOLEAN,
    list: ParamType.ARRAY,
    dict: ParamType.OBJECT,
}


def _infer_param_type(python_type: Optional[Type]) -> ParamType:
    """Infer ParamType from Python type annotation."""
    if python_type is None:
        return ParamType.ANY

    # Handle Optional types
    origin = getattr(python_type, "__origin__", None)
    if origin is Union:
        args = getattr(python_type, "__args__", ())
        # Filter out NoneType for Optional
        non_none_args = [a for a in args if a is not type(None)]
        if non_none_args:
            python_type = non_none_args[0]

    return _PYTHON_TYPE_MAP.get(python_type, ParamType.ANY)


def param(
    name: str,
    direction: Union[ParamDirection, str] = ParamDirection.INPUT,
    type: Union[ParamType, str, Type] = ParamType.STRING,
    required: bool = False,
    default: Any = None,
    description: str = "",
    choices: Optional[List[Any]] = None,
) -> Callable:
    """Decorator to define a parameter for a keyword.

    Use this decorator to add metadata to keyword parameters for documentation,
    validation, and UI generation.

    Args:
        name: Parameter name (must match function argument name for inputs)
        direction: 'input' or 'output' (or ParamDirection enum)
        type: Parameter type (ParamType enum, string, or Python type)
        required: Whether the parameter is required
        default: Default value if not provided
        description: Human-readable description
        choices: List of allowed values (optional)

    Usage:
        @keyword("Add Numbers")
        @param("a", type="number", required=True, description="First number")
        @param("b", type="number", required=True, description="Second number")
        @param("sum", direction="output", type="number", description="Result")
        def add_numbers(a: int, b: int) -> dict:
            return {"sum": a + b}
    """
    # Normalize direction
    if isinstance(direction, str):
        direction = ParamDirection(direction.lower())

    # Normalize type
    if isinstance(type, str):
        try:
            param_type = ParamType(type.lower())
        except ValueError:
            param_type = ParamType.ANY
    elif isinstance(type, ParamType):
        param_type = type
    elif isinstance(type, type.__class__):
        # It's a Python type (int, str, etc.)
        param_type = _infer_param_type(type)
    else:
        param_type = ParamType.ANY

    param_def = ParamDefinition(
        name=name,
        direction=direction,
        type=param_type,
        required=required,
        default=default,
        description=description,
        choices=choices,
    )

    def decorator(func: Callable) -> Callable:
        # Initialize params list if not exists
        if not hasattr(func, "_keyword_params"):
            func._keyword_params = []

        # Add param at beginning (decorators execute bottom-up)
        func._keyword_params.insert(0, param_def)
        return func

    return decorator


def input_param(
    name: str,
    type: Union[ParamType, str, Type] = ParamType.STRING,
    required: bool = False,
    default: Any = None,
    description: str = "",
    choices: Optional[List[Any]] = None,
) -> Callable:
    """Shorthand decorator for input parameters.

    Usage:
        @keyword("Greet User")
        @input_param("name", type="string", required=True, description="User's name")
        @input_param("greeting", default="Hello", description="Greeting prefix")
        def greet_user(name: str, greeting: str = "Hello") -> dict:
            return {"message": f"{greeting}, {name}!"}
    """
    return param(
        name=name,
        direction=ParamDirection.INPUT,
        type=type,
        required=required,
        default=default,
        description=description,
        choices=choices,
    )


def output_param(
    name: str,
    type: Union[ParamType, str, Type] = ParamType.STRING,
    description: str = "",
) -> Callable:
    """Shorthand decorator for output parameters.

    Usage:
        @keyword("Calculate Sum")
        @input_param("a", type="number", required=True)
        @input_param("b", type="number", required=True)
        @output_param("sum", type="number", description="The sum of a and b")
        def calculate_sum(a: int, b: int) -> dict:
            return {"sum": a + b}
    """
    return param(
        name=name,
        direction=ParamDirection.OUTPUT,
        type=type,
        required=False,
        description=description,
    )


def keyword(keyword_name: Optional[Union[str, Callable]] = None) -> Callable:
    """Decorator to register a function as a keyword.

    Can be used with or without parentheses, and with an optional custom name.
    Automatically collects parameter metadata from @param decorators and
    infers types from function signature when not explicitly defined.

    Usage:
        @keyword  # Uses function name
        def my_function():
            pass

        @keyword()  # Uses function name
        def my_function():
            pass

        @keyword("User Friendly Name")  # Uses custom name
        def technical_function_name():
            pass

        # With parameter decorators
        @keyword("Add Numbers")
        @param("a", type="number", required=True, description="First number")
        @param("b", type="number", required=True, description="Second number")
        @param("sum", direction="output", type="number")
        def add_numbers(a: int, b: int) -> dict:
            return {"sum": a + b}
    """

    def decorator(func: Callable) -> Callable:
        import logging

        logger = logging.getLogger(__name__)

        # Determine keyword name
        name = keyword_name if isinstance(keyword_name, str) else func.__name__

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        # Collect parameter definitions
        params: List[ParamDefinition] = []

        # Get explicitly defined params from @param decorators
        explicit_params = getattr(func, "_keyword_params", [])
        explicit_param_names = {p.name for p in explicit_params}
        params.extend(explicit_params)

        # Get function signature for validation and auto-discovery
        func_param_names: set = set()
        try:
            sig = inspect.signature(func)
            type_hints = getattr(func, "__annotations__", {})

            # Collect function parameter names (excluding *args, **kwargs)
            for param_name, param_obj in sig.parameters.items():
                if param_obj.kind not in (
                    inspect.Parameter.VAR_POSITIONAL,
                    inspect.Parameter.VAR_KEYWORD,
                ):
                    func_param_names.add(param_name)

            # Validate: Check if @input_param names match function arguments
            for explicit_param in explicit_params:
                if explicit_param.direction == ParamDirection.INPUT:
                    if explicit_param.name not in func_param_names:
                        logger.warning(
                            f"Keyword '{name}': @input_param '{explicit_param.name}' "
                            f"does not match any function argument. "
                            f"Available arguments: {sorted(func_param_names)}. "
                            f"This will cause errors at runtime!"
                        )

            # Auto-discover input params from function signature
            for param_name, param_obj in sig.parameters.items():
                if param_name in explicit_param_names:
                    continue  # Already defined explicitly

                # Skip *args and **kwargs
                if param_obj.kind in (
                    inspect.Parameter.VAR_POSITIONAL,
                    inspect.Parameter.VAR_KEYWORD,
                ):
                    continue

                # Infer type from annotation
                python_type = type_hints.get(param_name)
                param_type = _infer_param_type(python_type)

                # Check if required (no default value)
                is_required = param_obj.default == inspect.Parameter.empty
                default_val = None if is_required else param_obj.default

                auto_param = ParamDefinition(
                    name=param_name,
                    direction=ParamDirection.INPUT,
                    type=param_type,
                    required=is_required,
                    default=default_val,
                    description="",  # No description for auto-discovered
                )
                params.append(auto_param)

        except (ValueError, TypeError):
            pass  # Could not inspect signature

        # Store metadata on wrapper
        wrapper.keyword_name = name
        wrapper.keyword_params = params
        wrapper._keyword_params = params  # For compatibility

        # Register the keyword
        keyword_registry.register(wrapper)

        return wrapper

    # Handle both @keyword and @keyword() and @keyword("name")
    if callable(keyword_name):
        # Called as @keyword (without parentheses)
        func = keyword_name
        keyword_name = None
        return decorator(func)
    else:
        # Called as @keyword() or @keyword("name")
        return decorator


def get_keyword_schema(func: Callable) -> Dict[str, Any]:
    """Get the complete schema for a keyword function.

    Returns a dictionary with keyword metadata including name and parameters,
    useful for documentation generation or UI building.

    Args:
        func: A function decorated with @keyword

    Returns:
        Dictionary with keyword schema

    Usage:
        @keyword("My Keyword")
        @param("input1", type="string", required=True)
        def my_keyword(input1: str):
            pass

        schema = get_keyword_schema(my_keyword)
        # {
        #     "name": "My Keyword",
        #     "function": "my_keyword",
        #     "params": [{"name": "input1", "direction": "input", ...}]
        # }
    """
    return {
        "name": getattr(func, "keyword_name", func.__name__),
        "function": func.__name__,
        "doc": func.__doc__ or "",
        "params": [p.to_dict() for p in getattr(func, "keyword_params", [])],
    }


def get_all_keyword_schemas() -> List[Dict[str, Any]]:
    """Get schemas for all registered keywords.

    Returns:
        List of keyword schema dictionaries
    """
    schemas = []
    for name, func in keyword_registry.items():
        schemas.append(get_keyword_schema(func))
    return schemas


# ---- BeforeRun & AfterRun Hooks ----

before_run_hooks: List[Callable] = []
after_run_hooks: List[Callable] = []


def BeforeRun(func: Callable) -> Callable:
    """Decorator to register a function to run before each execution.

    Usage:
        @BeforeRun
        def setup_environment():
            print("Setting up...")
    """
    before_run_hooks.append(func)
    return func


def AfterRun(func: Callable) -> Callable:
    """Decorator to register a function to run after each execution.

    Usage:
        @AfterRun
        def cleanup():
            print("Cleaning up...")
    """
    after_run_hooks.append(func)
    return func
