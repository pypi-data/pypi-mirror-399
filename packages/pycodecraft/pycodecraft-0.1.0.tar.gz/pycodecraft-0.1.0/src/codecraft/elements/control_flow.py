"""Control flow statement nodes."""

from typing import Optional
from codecraft.core.node import Node


class IfNode(Node):
    """Node representing an if statement."""

    def __init__(self, condition: str, indent_level: int = 0):
        """
        Initialize an IfNode.

        Args:
            condition: The if condition
            indent_level: Indentation level
        """
        super().__init__(indent_level)
        self.condition = condition

    def render(self, indent_size: int = 4, indent_char: str = " ") -> str:
        """Render the if statement."""
        lines = []
        indent = self._get_indent(indent_size, indent_char)

        lines.append(f"{indent}if {self.condition}:")

        # Render children
        for child in self.children:
            rendered = child.render(indent_size, indent_char)
            # Don't filter out blank lines (empty strings are valid)
            if rendered is not None:
                lines.append(rendered)

        # If no children, add pass
        if not self.children:
            body_indent = indent_char * (indent_size * (self.indent_level + 1))
            lines.append(f"{body_indent}pass")

        return "\n".join(lines)


class ElifNode(Node):
    """Node representing an elif statement."""

    def __init__(self, condition: str, indent_level: int = 0):
        """
        Initialize an ElifNode.

        Args:
            condition: The elif condition
            indent_level: Indentation level
        """
        super().__init__(indent_level)
        self.condition = condition

    def render(self, indent_size: int = 4, indent_char: str = " ") -> str:
        """Render the elif statement."""
        lines = []
        indent = self._get_indent(indent_size, indent_char)

        lines.append(f"{indent}elif {self.condition}:")

        # Render children
        for child in self.children:
            rendered = child.render(indent_size, indent_char)
            # Don't filter out blank lines (empty strings are valid)
            if rendered is not None:
                lines.append(rendered)

        # If no children, add pass
        if not self.children:
            body_indent = indent_char * (indent_size * (self.indent_level + 1))
            lines.append(f"{body_indent}pass")

        return "\n".join(lines)


class ElseNode(Node):
    """Node representing an else statement."""

    def __init__(self, indent_level: int = 0):
        """
        Initialize an ElseNode.

        Args:
            indent_level: Indentation level
        """
        super().__init__(indent_level)

    def render(self, indent_size: int = 4, indent_char: str = " ") -> str:
        """Render the else statement."""
        lines = []
        indent = self._get_indent(indent_size, indent_char)

        lines.append(f"{indent}else:")

        # Render children
        for child in self.children:
            rendered = child.render(indent_size, indent_char)
            # Don't filter out blank lines (empty strings are valid)
            if rendered is not None:
                lines.append(rendered)

        # If no children, add pass
        if not self.children:
            body_indent = indent_char * (indent_size * (self.indent_level + 1))
            lines.append(f"{body_indent}pass")

        return "\n".join(lines)


class ForNode(Node):
    """Node representing a for loop."""

    def __init__(self, target: str, iterable: str, indent_level: int = 0):
        """
        Initialize a ForNode.

        Args:
            target: Loop variable name
            iterable: Iterable expression
            indent_level: Indentation level
        """
        super().__init__(indent_level)
        self.target = target
        self.iterable = iterable

    def render(self, indent_size: int = 4, indent_char: str = " ") -> str:
        """Render the for loop."""
        lines = []
        indent = self._get_indent(indent_size, indent_char)

        lines.append(f"{indent}for {self.target} in {self.iterable}:")

        # Render children
        for child in self.children:
            rendered = child.render(indent_size, indent_char)
            # Don't filter out blank lines (empty strings are valid)
            if rendered is not None:
                lines.append(rendered)

        # If no children, add pass
        if not self.children:
            body_indent = indent_char * (indent_size * (self.indent_level + 1))
            lines.append(f"{body_indent}pass")

        return "\n".join(lines)


class WhileNode(Node):
    """Node representing a while loop."""

    def __init__(self, condition: str, indent_level: int = 0):
        """
        Initialize a WhileNode.

        Args:
            condition: Loop condition
            indent_level: Indentation level
        """
        super().__init__(indent_level)
        self.condition = condition

    def render(self, indent_size: int = 4, indent_char: str = " ") -> str:
        """Render the while loop."""
        lines = []
        indent = self._get_indent(indent_size, indent_char)

        lines.append(f"{indent}while {self.condition}:")

        # Render children
        for child in self.children:
            rendered = child.render(indent_size, indent_char)
            # Don't filter out blank lines (empty strings are valid)
            if rendered is not None:
                lines.append(rendered)

        # If no children, add pass
        if not self.children:
            body_indent = indent_char * (indent_size * (self.indent_level + 1))
            lines.append(f"{body_indent}pass")

        return "\n".join(lines)


class TryNode(Node):
    """Node representing a try block."""

    def __init__(self, indent_level: int = 0):
        """
        Initialize a TryNode.

        Args:
            indent_level: Indentation level
        """
        super().__init__(indent_level)

    def render(self, indent_size: int = 4, indent_char: str = " ") -> str:
        """Render the try block."""
        lines = []
        indent = self._get_indent(indent_size, indent_char)

        lines.append(f"{indent}try:")

        # Render children
        for child in self.children:
            rendered = child.render(indent_size, indent_char)
            # Don't filter out blank lines (empty strings are valid)
            if rendered is not None:
                lines.append(rendered)

        # If no children, add pass
        if not self.children:
            body_indent = indent_char * (indent_size * (self.indent_level + 1))
            lines.append(f"{body_indent}pass")

        return "\n".join(lines)


class ExceptNode(Node):
    """Node representing an except block."""

    def __init__(
        self,
        exception: Optional[str] = None,
        as_: Optional[str] = None,
        indent_level: int = 0,
    ):
        """
        Initialize an ExceptNode.

        Args:
            exception: Exception type to catch (None for bare except)
            as_: Variable name to bind exception to
            indent_level: Indentation level
        """
        super().__init__(indent_level)
        self.exception = exception
        self.as_ = as_

    def render(self, indent_size: int = 4, indent_char: str = " ") -> str:
        """Render the except block."""
        lines = []
        indent = self._get_indent(indent_size, indent_char)

        # Build except line
        except_line = f"{indent}except"
        if self.exception:
            except_line += f" {self.exception}"
            if self.as_:
                except_line += f" as {self.as_}"
        except_line += ":"
        lines.append(except_line)

        # Render children
        for child in self.children:
            rendered = child.render(indent_size, indent_char)
            # Don't filter out blank lines (empty strings are valid)
            if rendered is not None:
                lines.append(rendered)

        # If no children, add pass
        if not self.children:
            body_indent = indent_char * (indent_size * (self.indent_level + 1))
            lines.append(f"{body_indent}pass")

        return "\n".join(lines)


class FinallyNode(Node):
    """Node representing a finally block."""

    def __init__(self, indent_level: int = 0):
        """
        Initialize a FinallyNode.

        Args:
            indent_level: Indentation level
        """
        super().__init__(indent_level)

    def render(self, indent_size: int = 4, indent_char: str = " ") -> str:
        """Render the finally block."""
        lines = []
        indent = self._get_indent(indent_size, indent_char)

        lines.append(f"{indent}finally:")

        # Render children
        for child in self.children:
            rendered = child.render(indent_size, indent_char)
            # Don't filter out blank lines (empty strings are valid)
            if rendered is not None:
                lines.append(rendered)

        # If no children, add pass
        if not self.children:
            body_indent = indent_char * (indent_size * (self.indent_level + 1))
            lines.append(f"{body_indent}pass")

        return "\n".join(lines)


class WithNode(Node):
    """Node representing a with statement."""

    def __init__(
        self, expression: str, as_: Optional[str] = None, indent_level: int = 0
    ):
        """
        Initialize a WithNode.

        Args:
            expression: Context manager expression
            as_: Variable name to bind to
            indent_level: Indentation level
        """
        super().__init__(indent_level)
        self.expression = expression
        self.as_ = as_

    def render(self, indent_size: int = 4, indent_char: str = " ") -> str:
        """Render the with statement."""
        lines = []
        indent = self._get_indent(indent_size, indent_char)

        # Build with line
        with_line = f"{indent}with {self.expression}"
        if self.as_:
            with_line += f" as {self.as_}"
        with_line += ":"
        lines.append(with_line)

        # Render children
        for child in self.children:
            rendered = child.render(indent_size, indent_char)
            # Don't filter out blank lines (empty strings are valid)
            if rendered is not None:
                lines.append(rendered)

        # If no children, add pass
        if not self.children:
            body_indent = indent_char * (indent_size * (self.indent_level + 1))
            lines.append(f"{body_indent}pass")

        return "\n".join(lines)
