"""Tests for the core CodeBuilder class."""

from codecraft import CodeBuilder


def test_codebuilder_creation():
    """Test basic CodeBuilder creation."""
    with CodeBuilder() as code:
        code.line("x = 1")

    result = code.generate()
    assert "x = 1" in result


def test_class_creation():
    """Test class creation."""
    with CodeBuilder() as code:
        with code.class_("MyClass"):
            code.attr("field", "str")

    result = code.generate()
    assert "class MyClass:" in result
    assert "field: str" in result


def test_class_with_bases():
    """Test class with base classes."""
    with CodeBuilder() as code:
        with code.class_("Child", bases=["Parent"]):
            code.line("pass")

    result = code.generate()
    assert "class Child(Parent):" in result


def test_class_with_decorators():
    """Test class with decorators."""
    with CodeBuilder() as code:
        with code.class_("MyClass", decorators=["@dataclass"]):
            code.attr("x", "int")

    result = code.generate()
    assert "@dataclass" in result
    assert "class MyClass:" in result


def test_function_creation():
    """Test function creation."""
    with CodeBuilder() as code:
        with code.function("my_func", params=["x: int"], returns="int"):
            code.line("return x * 2")

    result = code.generate()
    assert "def my_func(x: int) -> int:" in result
    assert "return x * 2" in result


def test_method_creation():
    """Test method creation."""
    with CodeBuilder() as code:
        with code.class_("MyClass"):
            with code.method("my_method", returns="str"):
                code.line("return 'hello'")

    result = code.generate()
    assert "def my_method(self) -> str:" in result


def test_if_statement():
    """Test if statement."""
    with CodeBuilder() as code:
        with code.if_("x > 0"):
            code.line("print('positive')")

    result = code.generate()
    assert "if x > 0:" in result
    assert "print('positive')" in result


def test_for_loop():
    """Test for loop."""
    with CodeBuilder() as code:
        with code.for_("item", "items"):
            code.line("process(item)")

    result = code.generate()
    assert "for item in items:" in result
    assert "process(item)" in result


def test_try_except():
    """Test try-except."""
    with CodeBuilder() as code:
        with code.try_():
            code.line("risky()")
        with code.except_("ValueError", "e"):
            code.line("handle(e)")

    result = code.generate()
    assert "try:" in result
    assert "except ValueError as e:" in result


def test_imports():
    """Test import handling."""
    with CodeBuilder() as code:
        code.add_import("os")
        code.add_from_import("typing", ["List", "Dict"])

    result = code.generate()
    assert "import os" in result
    assert "from typing import List, Dict" in result


def test_docstring():
    """Test docstring generation."""
    with CodeBuilder() as code:
        with code.class_("MyClass"):
            code.docstring("This is a class.")

    result = code.generate()
    assert '"""This is a class."""' in result


def test_blank_lines():
    """Test blank line insertion."""
    with CodeBuilder() as code:
        code.line("x = 1")
        code.blank_line()
        code.line("y = 2")

    result = code.generate()
    lines = result.split("\n")
    assert len(lines) >= 3


def test_indentation():
    """Test proper indentation."""
    with CodeBuilder(indent_size=2) as code:
        with code.class_("Test"):
            code.line("pass")

    result = code.generate()
    assert "  pass" in result  # 2 spaces


def test_validation_valid():
    """Test validation of valid code."""
    with CodeBuilder() as code:
        code.line("x = 1")

    assert code.validate() is True


def test_validation_invalid():
    """Test validation of invalid code."""
    with CodeBuilder() as code:
        code.line("def invalid syntax")

    assert code.validate() is False


def test_nested_classes():
    """Test nested class definitions."""
    with CodeBuilder() as code:
        with code.class_("Outer"):
            with code.class_("Inner"):
                code.attr("x", "int")

    result = code.generate()
    assert "class Outer:" in result
    assert "class Inner:" in result


def test_async_function():
    """Test async function generation."""
    with CodeBuilder() as code:
        with code.function("fetch", params=["url: str"], async_=True):
            code.line("return await get(url)")

    result = code.generate()
    assert "async def fetch(url: str):" in result
