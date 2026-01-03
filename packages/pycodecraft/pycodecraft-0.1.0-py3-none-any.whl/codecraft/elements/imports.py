"""Import statement nodes."""

from typing import List, Optional, Set
from codecraft.core.node import Node


class ImportNode(Node):
    """Node representing an import statement (import x, import x as y)."""

    def __init__(self, module: str, alias: Optional[str] = None):
        """
        Initialize an ImportNode.

        Args:
            module: The module to import
            alias: Optional alias for the import
        """
        super().__init__(0)  # Imports are never indented
        self.module = module
        self.alias = alias

    def render(self, indent_size: int = 4, indent_char: str = " ") -> str:
        """Render the import statement."""
        if self.alias:
            return f"import {self.module} as {self.alias}"
        return f"import {self.module}"

    def __eq__(self, other) -> bool:
        """Check equality for deduplication."""
        if not isinstance(other, ImportNode):
            return False
        return self.module == other.module and self.alias == other.alias

    def __hash__(self) -> int:
        """Hash for use in sets."""
        return hash((self.module, self.alias))


class FromImportNode(Node):
    """Node representing a from-import statement (from x import y, z)."""

    def __init__(self, module: str, items: List[str]):
        """
        Initialize a FromImportNode.

        Args:
            module: The module to import from
            items: List of items to import
        """
        super().__init__(0)  # Imports are never indented
        self.module = module
        self.items = items if isinstance(items, list) else [items]

    def render(self, indent_size: int = 4, indent_char: str = " ") -> str:
        """Render the from-import statement."""
        items_str = ", ".join(self.items)
        return f"from {self.module} import {items_str}"

    def __eq__(self, other) -> bool:
        """Check equality for deduplication."""
        if not isinstance(other, FromImportNode):
            return False
        return self.module == other.module and set(self.items) == set(other.items)

    def __hash__(self) -> int:
        """Hash for use in sets."""
        return hash((self.module, tuple(sorted(self.items))))


class ImportManager:
    """Manages imports and handles deduplication."""

    def __init__(self):
        """Initialize the ImportManager."""
        self._imports: Set[ImportNode] = set()
        self._from_imports: Set[FromImportNode] = set()

    def add_import(self, module: str, alias: Optional[str] = None) -> None:
        """
        Add a regular import.

        Args:
            module: The module to import
            alias: Optional alias
        """
        self._imports.add(ImportNode(module, alias))

    def add_from_import(self, module: str, items: List[str]) -> None:
        """
        Add a from-import.

        Args:
            module: The module to import from
            items: Items to import
        """
        # Check if we already have a from-import for this module
        existing = None
        for imp in self._from_imports:
            if imp.module == module:
                existing = imp
                break

        if existing:
            # Merge items
            self._from_imports.remove(existing)
            merged_items = list(set(existing.items + items))
            self._from_imports.add(FromImportNode(module, merged_items))
        else:
            self._from_imports.add(FromImportNode(module, items))

    def get_import_nodes(self) -> List[Node]:
        """
        Get all import nodes sorted.

        Returns:
            List of import nodes sorted by module name
        """
        all_imports = []

        # Sort regular imports
        sorted_imports = sorted(self._imports, key=lambda x: x.module)
        all_imports.extend(sorted_imports)

        # Sort from-imports
        sorted_from_imports = sorted(self._from_imports, key=lambda x: x.module)
        all_imports.extend(sorted_from_imports)

        return all_imports

    def clear(self) -> None:
        """Clear all imports."""
        self._imports.clear()
        self._from_imports.clear()
