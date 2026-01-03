"""Class definition nodes."""

from typing import List, Optional
from codecraft.core.node import Node
from codecraft.utils import format_bases
from codecraft.elements.decorators import render_decorators


class AttributeNode(Node):
    """Node representing a class attribute with type annotation."""

    def __init__(
        self,
        name: str,
        type_hint: str,
        default: Optional[str] = None,
        indent_level: int = 1,
    ):
        """
        Initialize an AttributeNode.

        Args:
            name: Attribute name
            type_hint: Type annotation
            default: Default value (optional)
            indent_level: Indentation level
        """
        super().__init__(indent_level)
        self.name = name
        self.type_hint = type_hint
        self.default = default

    def render(self, indent_size: int = 4, indent_char: str = " ") -> str:
        """Render the attribute."""
        indent = self._get_indent(indent_size, indent_char)

        if self.default:
            return f"{indent}{self.name}: {self.type_hint} = {self.default}"
        return f"{indent}{self.name}: {self.type_hint}"


class ClassNode(Node):
    """Node representing a class definition."""

    def __init__(
        self,
        name: str,
        bases: Optional[List[str]] = None,
        decorators: Optional[List[str]] = None,
        indent_level: int = 0,
    ):
        """
        Initialize a ClassNode.

        Args:
            name: Class name
            bases: List of base classes
            decorators: List of decorators
            indent_level: Indentation level
        """
        super().__init__(indent_level)
        self.name = name
        self.bases = bases or []
        self.decorators = decorators or []
        self.attributes: List[AttributeNode] = []
        self.docstring: Optional[str] = None

    def add_attribute(
        self, name: str, type_hint: str, default: Optional[str] = None
    ) -> None:
        """
        Add an attribute to the class.

        Args:
            name: Attribute name
            type_hint: Type annotation
            default: Default value
        """
        attr = AttributeNode(name, type_hint, default, self.indent_level + 1)
        self.attributes.append(attr)

    def set_docstring(self, text: str) -> None:
        """
        Set the class docstring.

        Args:
            text: Docstring text
        """
        self.docstring = text

    def render(self, indent_size: int = 4, indent_char: str = " ") -> str:
        """Render the class definition."""
        lines = []
        indent = self._get_indent(indent_size, indent_char)
        body_indent = indent_char * (indent_size * (self.indent_level + 1))

        # Render decorators
        if self.decorators:
            dec_lines = render_decorators(
                self.decorators, self.indent_level, indent_size, indent_char
            )
            lines.extend(dec_lines)

        # Class definition line
        bases_str = format_bases(self.bases)
        lines.append(f"{indent}class {self.name}{bases_str}:")

        # Docstring - render BEFORE attributes (Python convention)
        if self.docstring:
            if "\n" not in self.docstring:
                lines.append(f'{body_indent}"""{self.docstring}"""')
            else:
                lines.append(f'{body_indent}"""')
                for line in self.docstring.split("\n"):
                    lines.append(f"{body_indent}{line}")
                lines.append(f'{body_indent}"""')

        # Attributes - render AFTER docstring
        for attr in self.attributes:
            lines.append(attr.render(indent_size, indent_char))

        # Children (methods, nested classes, etc.)
        for child in self.children:
            rendered = child.render(indent_size, indent_char)
            # Don't filter out blank lines (empty strings are valid)
            if rendered is not None:
                lines.append(rendered)

        # If class is empty, add pass
        if not self.docstring and not self.attributes and not self.children:
            lines.append(f"{body_indent}pass")

        return "\n".join(lines)
