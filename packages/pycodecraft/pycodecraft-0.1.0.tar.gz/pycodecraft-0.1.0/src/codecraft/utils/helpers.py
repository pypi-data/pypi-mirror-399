"""Utility functions for code generation."""

from typing import List, Optional


def format_params(params: List[str]) -> str:
    """
    Format a list of parameters for function/method signatures.

    Args:
        params: List of parameter strings (e.g., ["self", "name: str", "age: int = 0"])

    Returns:
        Formatted parameter string
    """
    return ", ".join(params)


def format_type_hint(type_hint: Optional[str]) -> str:
    """
    Format a type hint string.

    Args:
        type_hint: The type hint string

    Returns:
        Formatted type hint with colon prefix, or empty string if None
    """
    if type_hint:
        return f": {type_hint}"
    return ""


def format_return_type(return_type: Optional[str]) -> str:
    """
    Format a return type annotation.

    Args:
        return_type: The return type string

    Returns:
        Formatted return type with arrow, or empty string if None
    """
    if return_type:
        return f" -> {return_type}"
    return ""


def format_bases(bases: List[str]) -> str:
    """
    Format base classes for class definition.

    Args:
        bases: List of base class names

    Returns:
        Formatted bases string with parentheses, or empty string if no bases
    """
    if bases:
        return f"({', '.join(bases)})"
    return ""


def ensure_list(value) -> List:
    """
    Ensure a value is a list.

    Args:
        value: A value that might be a list, None, or a single item

    Returns:
        A list containing the value(s)
    """
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]
