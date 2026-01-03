"""Function and method definition nodes."""

from typing import List, Optional
from codecraft.core.node import Node
from codecraft.utils import format_params, format_return_type
from codecraft.elements.decorators import render_decorators


class FunctionNode(Node):
    """Node representing a function definition."""

    def __init__(
        self,
        name: str,
        params: Optional[List[str]] = None,
        returns: Optional[str] = None,
        decorators: Optional[List[str]] = None,
        async_: bool = False,
        indent_level: int = 0,
    ):
        """
        Initialize a FunctionNode.

        Args:
            name: Function name
            params: List of parameter strings
            returns: Return type annotation
            decorators: List of decorators
            async_: Whether this is an async function
            indent_level: Indentation level
        """
        super().__init__(indent_level)
        self.name = name
        self.params = params or []
        self.returns = returns
        self.decorators = decorators or []
        self.async_ = async_
        self.docstring: Optional[str] = None

    def set_docstring(self, text: str) -> None:
        """
        Set the function docstring.

        Args:
            text: Docstring text
        """
        self.docstring = text

    def render(self, indent_size: int = 4, indent_char: str = " ") -> str:
        """Render the function definition."""
        lines = []
        indent = self._get_indent(indent_size, indent_char)
        body_indent = indent_char * (indent_size * (self.indent_level + 1))

        # Render decorators
        if self.decorators:
            dec_lines = render_decorators(
                self.decorators, self.indent_level, indent_size, indent_char
            )
            lines.extend(dec_lines)

        # Function definition line
        async_prefix = "async " if self.async_ else ""
        params_str = format_params(self.params)
        return_str = format_return_type(self.returns)
        lines.append(
            f"{indent}{async_prefix}def {self.name}({params_str}){return_str}:"
        )

        # Docstring
        if self.docstring:
            if "\n" not in self.docstring:
                lines.append(f'{body_indent}"""{self.docstring}"""')
            else:
                lines.append(f'{body_indent}"""')
                for line in self.docstring.split("\n"):
                    lines.append(f"{body_indent}{line}")
                lines.append(f'{body_indent}"""')

        # Body (children)
        for child in self.children:
            rendered = child.render(indent_size, indent_char)
            if rendered:
                lines.append(rendered)

        # If function is empty, add pass
        if not self.docstring and not self.children:
            lines.append(f"{body_indent}pass")

        return "\n".join(lines)


class MethodNode(FunctionNode):
    """
    Node representing a method definition (same as function but conceptually different).

    Methods typically have 'self' or 'cls' as first parameter.
    """

    def __init__(
        self,
        name: str,
        params: Optional[List[str]] = None,
        returns: Optional[str] = None,
        decorators: Optional[List[str]] = None,
        async_: bool = False,
        indent_level: int = 1,
    ):
        """
        Initialize a MethodNode.

        Args:
            name: Method name
            params: List of parameter strings (should include self/cls)
            returns: Return type annotation
            decorators: List of decorators
            async_: Whether this is an async method
            indent_level: Indentation level (default 1 for class methods)
        """
        # Ensure 'self' is in params if not provided
        if not params:
            params = ["self"]
        elif "self" not in params[0] and "cls" not in params[0]:
            params = ["self"] + params

        super().__init__(name, params, returns, decorators, async_, indent_level)
