"""Indentation management for code generation."""

from contextlib import contextmanager
from typing import Generator


class IndentationManager:
    """
    Manages indentation levels for code generation.

    Provides methods to track and manipulate indentation levels,
    and generate indentation strings.
    """

    def __init__(self, size: int = 4, char: str = " "):
        """
        Initialize the IndentationManager.

        Args:
            size: Number of characters per indentation level
            char: Character to use for indentation (space or tab)
        """
        self.size = size
        self.char = char
        self.level = 0

    def indent(self) -> str:
        """
        Get the current indentation string.

        Returns:
            String of indentation characters for current level
        """
        return self.char * (self.size * self.level)

    def increase(self) -> None:
        """Increase the indentation level by one."""
        self.level += 1

    def decrease(self) -> None:
        """Decrease the indentation level by one (minimum 0)."""
        self.level = max(0, self.level - 1)

    @contextmanager
    def indented(self) -> Generator[None, None, None]:
        """
        Context manager for temporarily increasing indentation.

        Usage:
            with indent_manager.indented():
                # Code here is indented one level deeper
                pass
        """
        self.increase()
        try:
            yield
        finally:
            self.decrease()
