"""Main CodeBuilder class for code generation."""

from typing import List, Optional
from contextlib import contextmanager

from codecraft.core.node import (
    Node,
    RawLineNode,
    BlankLineNode,
    CommentNode,
    DocstringNode,
)
from codecraft.core.context import ClassContext, FunctionContext, ControlFlowContext
from codecraft.elements.imports import ImportManager
from codecraft.utils import IndentationManager


class CodeBuilder:
    """
    Main code builder class using context managers.

    This is the entry point for all code generation. Use it as a context
    manager to build Python code programmatically.

    Example:
        ```python
        with CodeBuilder() as code:
            with code.class_("MyClass"):
                code.attr("name", "str")
        print(code.generate())
        ```
    """

    def __init__(self, indent_size: int = 4, indent_char: str = " "):
        """
        Initialize the CodeBuilder.

        Args:
            indent_size: Number of characters per indentation level
            indent_char: Character to use for indentation (space or tab)
        """
        self._nodes: List[Node] = []
        self._indent_manager = IndentationManager(indent_size, indent_char)
        self._indent_size = indent_size
        self._indent_char = indent_char
        self._import_manager = ImportManager()
        self._context_stack: List = []

    def __enter__(self) -> "CodeBuilder":
        """Enter the context."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context."""
        pass

    # Context stack management
    def _push_context(self, context):
        """Push a context onto the stack."""
        self._context_stack.append(context)

    def _pop_context(self):
        """Pop a context from the stack."""
        if self._context_stack:
            self._context_stack.pop()

    def _current_context(self):
        """Get the current context or None."""
        return self._context_stack[-1] if self._context_stack else None

    def _add_node(self, node: Node):
        """Add a node to the current context or root."""
        current = self._current_context()
        if current and hasattr(current, "node") and current.node:
            current.node.add_child(node)
        else:
            self._nodes.append(node)

    # Context managers for structural elements
    @contextmanager
    def class_(
        self,
        name: str,
        bases: Optional[List[str]] = None,
        decorators: Optional[List[str]] = None,
    ):
        """
        Context manager for class definition.

        Args:
            name: Class name
            bases: List of base class names
            decorators: List of decorator strings

        Yields:
            ClassContext: The class context
        """
        ctx = ClassContext(self, name, bases, decorators)
        with ctx:
            yield ctx

    @contextmanager
    def function(
        self,
        name: str,
        params: Optional[List[str]] = None,
        returns: Optional[str] = None,
        decorators: Optional[List[str]] = None,
        async_: bool = False,
    ):
        """
        Context manager for function definition.

        Args:
            name: Function name
            params: List of parameter strings
            returns: Return type annotation
            decorators: List of decorator strings
            async_: Whether this is an async function

        Yields:
            FunctionContext: The function context
        """
        ctx = FunctionContext(
            self, name, params, returns, decorators, async_, is_method=False
        )
        with ctx:
            yield ctx

    @contextmanager
    def method(
        self,
        name: str,
        params: Optional[List[str]] = None,
        returns: Optional[str] = None,
        decorators: Optional[List[str]] = None,
        async_: bool = False,
    ):
        """
        Context manager for method definition.

        Args:
            name: Method name
            params: List of parameter strings (will add 'self' if missing)
            returns: Return type annotation
            decorators: List of decorator strings
            async_: Whether this is an async method

        Yields:
            FunctionContext: The method context
        """
        ctx = FunctionContext(
            self, name, params, returns, decorators, async_, is_method=True
        )
        with ctx:
            yield ctx

    # Control flow context managers
    @contextmanager
    def if_(self, condition: str):
        """
        Context manager for if statement.

        Args:
            condition: The if condition

        Yields:
            ControlFlowContext: The if context
        """
        from codecraft.elements.control_flow import IfNode

        node = IfNode(condition, self._indent_manager.level)
        ctx = ControlFlowContext(self, node)
        with ctx:
            yield ctx

    @contextmanager
    def elif_(self, condition: str):
        """
        Context manager for elif statement.

        Args:
            condition: The elif condition

        Yields:
            ControlFlowContext: The elif context
        """
        from codecraft.elements.control_flow import ElifNode

        node = ElifNode(condition, self._indent_manager.level)
        ctx = ControlFlowContext(self, node)
        with ctx:
            yield ctx

    @contextmanager
    def else_(self):
        """
        Context manager for else statement.

        Yields:
            ControlFlowContext: The else context
        """
        from codecraft.elements.control_flow import ElseNode

        node = ElseNode(self._indent_manager.level)
        ctx = ControlFlowContext(self, node)
        with ctx:
            yield ctx

    @contextmanager
    def for_(self, target: str, iterable: str):
        """
        Context manager for for loop.

        Args:
            target: Loop variable name
            iterable: Iterable expression

        Yields:
            ControlFlowContext: The for loop context
        """
        from codecraft.elements.control_flow import ForNode

        node = ForNode(target, iterable, self._indent_manager.level)
        ctx = ControlFlowContext(self, node)
        with ctx:
            yield ctx

    @contextmanager
    def while_(self, condition: str):
        """
        Context manager for while loop.

        Args:
            condition: Loop condition

        Yields:
            ControlFlowContext: The while loop context
        """
        from codecraft.elements.control_flow import WhileNode

        node = WhileNode(condition, self._indent_manager.level)
        ctx = ControlFlowContext(self, node)
        with ctx:
            yield ctx

    @contextmanager
    def try_(self):
        """
        Context manager for try block.

        Yields:
            ControlFlowContext: The try context
        """
        from codecraft.elements.control_flow import TryNode

        node = TryNode(self._indent_manager.level)
        ctx = ControlFlowContext(self, node)
        with ctx:
            yield ctx

    @contextmanager
    def except_(self, exception: Optional[str] = None, as_: Optional[str] = None):
        """
        Context manager for except block.

        Args:
            exception: Exception type to catch
            as_: Variable name to bind exception to

        Yields:
            ControlFlowContext: The except context
        """
        from codecraft.elements.control_flow import ExceptNode

        node = ExceptNode(exception, as_, self._indent_manager.level)
        ctx = ControlFlowContext(self, node)
        with ctx:
            yield ctx

    @contextmanager
    def finally_(self):
        """
        Context manager for finally block.

        Yields:
            ControlFlowContext: The finally context
        """
        from codecraft.elements.control_flow import FinallyNode

        node = FinallyNode(self._indent_manager.level)
        ctx = ControlFlowContext(self, node)
        with ctx:
            yield ctx

    @contextmanager
    def with_(self, expression: str, as_: Optional[str] = None):
        """
        Context manager for with statement.

        Args:
            expression: Context manager expression
            as_: Variable name to bind to

        Yields:
            ControlFlowContext: The with context
        """
        from codecraft.elements.control_flow import WithNode

        node = WithNode(expression, as_, self._indent_manager.level)
        ctx = ControlFlowContext(self, node)
        with ctx:
            yield ctx

    # Direct code operations
    def line(self, code: str):
        """
        Add a raw line of code.

        Args:
            code: The code line
        """
        node = RawLineNode(code, self._indent_manager.level)
        self._add_node(node)

    def return_(self, value: str):
        """
        Add a return statement.

        Args:
            value: The value to return
        """
        node = RawLineNode(f"return {value}", self._indent_manager.level)
        self._add_node(node)

    def raw(self, code: str):
        """
        Add raw unindented code.

        Args:
            code: The raw code
        """
        node = RawLineNode(code, 0)
        self._add_node(node)

    def comment(self, text: str):
        """
        Add a comment.

        Args:
            text: Comment text (without # prefix)
        """
        node = CommentNode(text, self._indent_manager.level)
        self._add_node(node)

    def docstring(self, text: str):
        """
        Add a docstring.

        If called within a class or function context, sets the docstring on that element.
        Otherwise, adds a standalone docstring node.

        Args:
            text: Docstring text
        """
        current = self._current_context()

        # If we're in a ClassContext or FunctionContext, use their docstring method
        if current and hasattr(current, "docstring"):
            current.docstring(text)
        else:
            # Standalone docstring (module-level, etc.)
            node = DocstringNode(text, self._indent_manager.level)
            self._add_node(node)

    def blank_line(self):
        """Add a single blank line."""
        self._add_node(BlankLineNode())

    def blank_lines(self, n: int):
        """
        Add multiple blank lines.

        Args:
            n: Number of blank lines to add
        """
        for _ in range(n):
            self.blank_line()

    def attr(self, name: str, type_: str, default: Optional[str] = None):
        """
        Add an attribute (for use within class context).

        Args:
            name: Attribute name
            type_: Type annotation
            default: Default value
        """
        current = self._current_context()
        if isinstance(current, ClassContext):
            current.attr(name, type_, default)
        else:
            raise RuntimeError("attr() can only be used within a class context")

    # Import operations
    def add_import(self, module: str, items: Optional[List[str]] = None):
        """
        Add an import statement.

        If called within a context (if, for, class, etc.), adds the import as a code line.
        Otherwise, adds to the global import manager at the top of the file.

        Args:
            module: Module to import
            items: Optional items to import from module
        """
        # If we're inside a context, add as a code line instead of to import manager
        if self._current_context():
            if items:
                items_str = ", ".join(items)
                self.line(f"from {module} import {items_str}")
            else:
                self.line(f"import {module}")
        else:
            # Top-level imports go to the import manager
            if items:
                self._import_manager.add_from_import(module, items)
            else:
                self._import_manager.add_import(module)

    def add_from_import(self, module: str, items: List[str]):
        """
        Add a from-import statement.

        If called within a context (if, for, class, etc.), adds the import as a code line.
        Otherwise, adds to the global import manager at the top of the file.

        Args:
            module: Module to import from
            items: Items to import
        """
        # If we're inside a context, add as a code line instead of to import manager
        if self._current_context():
            items_str = ", ".join(items)
            self.line(f"from {module} import {items_str}")
        else:
            # Top-level imports go to the import manager
            self._import_manager.add_from_import(module, items)

    # Code generation
    def generate(self, format: bool = False, line_length: int = 88) -> str:
        """
        Generate the Python code as a string.

        Args:
            format: Whether to format with black
            line_length: Line length for formatting

        Returns:
            The generated Python code
        """
        lines = []

        # Add imports first
        import_nodes = self._import_manager.get_import_nodes()
        for imp in import_nodes:
            lines.append(imp.render(self._indent_size, self._indent_char))

        # Add blank lines after imports if we have them
        if import_nodes and self._nodes:
            lines.append("")
            lines.append("")

        # Render all nodes - don't filter out blank lines (empty strings are valid)
        for node in self._nodes:
            rendered = node.render(self._indent_size, self._indent_char)
            # Check for None instead of falsy to allow empty strings (blank lines)
            if rendered is not None:
                lines.append(rendered)

        code = "\n".join(lines)

        # Format if requested
        if format:
            try:
                import black

                code = black.format_str(code, mode=black.Mode(line_length=line_length))
            except ImportError:
                pass  # black not installed, skip formatting

        return code

    def save(self, filepath: str, format: bool = True, line_length: int = 88):
        """
        Save the generated code to a file.

        Args:
            filepath: Path to save to
            format: Whether to format with black
            line_length: Line length for formatting
        """
        code = self.generate(format, line_length)
        with open(filepath, "w") as f:
            f.write(code)

    def validate(self, detailed: bool = False):
        """
        Validate the generated Python code.

        Args:
            detailed: Whether to return detailed validation results

        Returns:
            bool or dict: True if valid, or dict with validation details
        """
        code = self.generate()

        try:
            compile(code, "<string>", "exec")
            if detailed:
                return {"valid": True, "errors": [], "warnings": []}
            return True
        except SyntaxError as e:
            if detailed:
                return {
                    "valid": False,
                    "errors": [f"Syntax error at line {e.lineno}: {e.msg}"],
                    "warnings": [],
                }
            return False
