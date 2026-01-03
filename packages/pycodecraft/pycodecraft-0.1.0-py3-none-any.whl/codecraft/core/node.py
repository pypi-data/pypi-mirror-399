"""Base Node class for all code elements."""

from abc import ABC, abstractmethod
from typing import List, Optional


class Node(ABC):
    """
    Abstract base class for all code elements in the AST.

    Each node represents a piece of Python code and can render itself
    with proper indentation and formatting.
    """

    def __init__(self, indent_level: int = 0):
        """
        Initialize a Node.

        Args:
            indent_level: The indentation level for this node
        """
        self.indent_level = indent_level
        self.children: List[Node] = []

    @abstractmethod
    def render(self, indent_size: int = 4, indent_char: str = " ") -> str:
        """
        Render this node as Python code.

        Args:
            indent_size: Number of indent characters per level
            indent_char: Character to use for indentation

        Returns:
            The rendered Python code as a string
        """
        pass

    def add_child(self, node: "Node") -> None:
        """
        Add a child node.

        Args:
            node: The child node to add
        """
        self.children.append(node)

    def _get_indent(self, indent_size: int = 4, indent_char: str = " ") -> str:
        """
        Get the indentation string for this node.

        Args:
            indent_size: Number of indent characters per level
            indent_char: Character to use for indentation

        Returns:
            The indentation string
        """
        return indent_char * (indent_size * self.indent_level)


class RawLineNode(Node):
    """Node representing a raw line of code."""

    def __init__(self, code: str, indent_level: int = 0):
        """
        Initialize a RawLineNode.

        Args:
            code: The raw code line
            indent_level: The indentation level
        """
        super().__init__(indent_level)
        self.code = code

    def render(self, indent_size: int = 4, indent_char: str = " ") -> str:
        """Render the raw line with proper indentation."""
        if not self.code.strip():
            return ""
        indent = self._get_indent(indent_size, indent_char)
        return f"{indent}{self.code}"


class BlankLineNode(Node):
    """Node representing a blank line."""

    def __init__(self):
        """Initialize a BlankLineNode."""
        super().__init__(0)

    def render(self, indent_size: int = 4, indent_char: str = " ") -> str:
        """Render a blank line."""
        return ""


class CommentNode(Node):
    """Node representing a comment."""

    def __init__(self, text: str, indent_level: int = 0):
        """
        Initialize a CommentNode.

        Args:
            text: The comment text (without # prefix)
            indent_level: The indentation level
        """
        super().__init__(indent_level)
        self.text = text

    def render(self, indent_size: int = 4, indent_char: str = " ") -> str:
        """Render the comment."""
        indent = self._get_indent(indent_size, indent_char)
        return f"{indent}# {self.text}"


class DocstringNode(Node):
    """Node representing a docstring."""

    def __init__(self, text: str, indent_level: int = 0):
        """
        Initialize a DocstringNode.

        Args:
            text: The docstring text
            indent_level: The indentation level
        """
        super().__init__(indent_level)
        self.text = text

    def render(self, indent_size: int = 4, indent_char: str = " ") -> str:
        """Render the docstring."""
        indent = self._get_indent(indent_size, indent_char)

        # Single line docstring
        if "\n" not in self.text:
            return f'{indent}"""{self.text}"""'

        # Multi-line docstring
        lines = [f'{indent}"""']
        for line in self.text.split("\n"):
            lines.append(f"{indent}{line}")
        lines.append(f'{indent}"""')
        return "\n".join(lines)
