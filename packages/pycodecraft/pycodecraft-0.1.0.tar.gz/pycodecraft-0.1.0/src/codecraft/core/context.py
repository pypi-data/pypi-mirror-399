"""Context managers for code generation."""

from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from codecraft.core.builder import CodeBuilder


class BaseContext:
    """Base context manager class."""

    def __init__(self, builder: "CodeBuilder"):
        """
        Initialize the context.

        Args:
            builder: The CodeBuilder instance
        """
        self.builder = builder
        self.node = None

    def __enter__(self) -> "BaseContext":
        """Enter the context."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context."""
        pass


class ClassContext(BaseContext):
    """Context manager for class definitions."""

    def __init__(
        self,
        builder: "CodeBuilder",
        name: str,
        bases: Optional[List[str]] = None,
        decorators: Optional[List[str]] = None,
    ):
        """
        Initialize a ClassContext.

        Args:
            builder: The CodeBuilder instance
            name: Class name
            bases: Base classes
            decorators: Class decorators
        """
        super().__init__(builder)
        from codecraft.elements.class_element import ClassNode

        self.node = ClassNode(name, bases, decorators, builder._indent_manager.level)

    def __enter__(self) -> "ClassContext":
        """Enter the class context."""
        self.builder._add_node(self.node)  # Add node first
        self.builder._push_context(self)  # Then push context
        self.builder._indent_manager.increase()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the class context."""
        self.builder._indent_manager.decrease()
        self.builder._pop_context()

    def attr(self, name: str, type_: str, default: Optional[str] = None):
        """
        Add an attribute to the class.

        Args:
            name: Attribute name
            type_: Type annotation
            default: Default value
        """
        self.node.add_attribute(name, type_, default)

    def docstring(self, text: str):
        """
        Set the class docstring.

        Args:
            text: Docstring text
        """
        self.node.set_docstring(text)


class FunctionContext(BaseContext):
    """Context manager for function definitions."""

    def __init__(
        self,
        builder: "CodeBuilder",
        name: str,
        params: Optional[List[str]] = None,
        returns: Optional[str] = None,
        decorators: Optional[List[str]] = None,
        async_: bool = False,
        is_method: bool = False,
    ):
        """
        Initialize a FunctionContext.

        Args:
            builder: The CodeBuilder instance
            name: Function name
            params: Parameters
            returns: Return type
            decorators: Function decorators
            async_: Whether async function
            is_method: Whether this is a method
        """
        super().__init__(builder)
        from codecraft.elements.function_element import FunctionNode, MethodNode

        if is_method:
            self.node = MethodNode(
                name, params, returns, decorators, async_, builder._indent_manager.level
            )
        else:
            self.node = FunctionNode(
                name, params, returns, decorators, async_, builder._indent_manager.level
            )

    def __enter__(self) -> "FunctionContext":
        """Enter the function context."""
        self.builder._add_node(self.node)  # Add node first
        self.builder._push_context(self)  # Then push context
        self.builder._indent_manager.increase()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the function context."""
        self.builder._indent_manager.decrease()
        self.builder._pop_context()

    def docstring(self, text: str):
        """
        Set the function docstring.

        Args:
            text: Docstring text
        """
        self.node.set_docstring(text)


class ControlFlowContext(BaseContext):
    """Context manager for control flow statements."""

    def __init__(self, builder: "CodeBuilder", node):
        """
        Initialize a ControlFlowContext.

        Args:
            builder: The CodeBuilder instance
            node: The control flow node
        """
        super().__init__(builder)
        self.node = node

    def __enter__(self) -> "ControlFlowContext":
        """Enter the control flow context."""
        self.builder._add_node(self.node)  # Add node first
        self.builder._push_context(self)  # Then push context
        self.builder._indent_manager.increase()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the control flow context."""
        self.builder._indent_manager.decrease()
        self.builder._pop_context()
