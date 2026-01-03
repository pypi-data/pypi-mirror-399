"""Decorator support for classes and functions."""

from typing import List
from codecraft.core.node import Node


class DecoratorNode(Node):
    """Node representing a decorator."""

    def __init__(self, name: str, indent_level: int = 0):
        """
        Initialize a DecoratorNode.

        Args:
            name: The decorator name (with @ prefix)
            indent_level: The indentation level
        """
        super().__init__(indent_level)
        # Ensure decorator starts with @
        self.name = name if name.startswith("@") else f"@{name}"

    def render(self, indent_size: int = 4, indent_char: str = " ") -> str:
        """Render the decorator."""
        indent = self._get_indent(indent_size, indent_char)
        return f"{indent}{self.name}"


def render_decorators(
    decorators: List[str],
    indent_level: int,
    indent_size: int = 4,
    indent_char: str = " ",
) -> List[str]:
    """
    Render a list of decorator strings.

    Args:
        decorators: List of decorator strings
        indent_level: Indentation level
        indent_size: Indent size
        indent_char: Indent character

    Returns:
        List of rendered decorator lines
    """
    lines = []
    for dec in decorators:
        node = DecoratorNode(dec, indent_level)
        lines.append(node.render(indent_size, indent_char))
    return lines
