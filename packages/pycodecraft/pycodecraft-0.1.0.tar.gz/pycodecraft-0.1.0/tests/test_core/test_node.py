"""Tests for Node classes."""

from codecraft.core.node import RawLineNode, BlankLineNode, CommentNode, DocstringNode


def test_raw_line_node():
    """Test RawLineNode rendering."""
    node = RawLineNode("x = 1", indent_level=0)
    assert node.render() == "x = 1"


def test_raw_line_node_indented():
    """Test RawLineNode with indentation."""
    node = RawLineNode("x = 1", indent_level=1)
    assert node.render(indent_size=4) == "    x = 1"


def test_blank_line_node():
    """Test BlankLineNode rendering."""
    node = BlankLineNode()
    assert node.render() == ""


def test_comment_node():
    """Test CommentNode rendering."""
    node = CommentNode("This is a comment", indent_level=0)
    assert node.render() == "# This is a comment"


def test_docstring_node_single_line():
    """Test DocstringNode single line."""
    node = DocstringNode("Single line docstring", indent_level=0)
    result = node.render()
    assert '"""Single line docstring"""' in result


def test_docstring_node_multi_line():
    """Test DocstringNode multi-line."""
    node = DocstringNode("Line 1\nLine 2", indent_level=0)
    result = node.render()
    assert '"""' in result
    assert "Line 1" in result
    assert "Line 2" in result
