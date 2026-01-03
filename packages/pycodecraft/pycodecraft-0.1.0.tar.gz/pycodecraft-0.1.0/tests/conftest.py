"""Shared test fixtures."""

import pytest
from codecraft import CodeBuilder


@pytest.fixture
def code_builder():
    """Create a CodeBuilder instance for testing."""
    with CodeBuilder() as builder:
        yield builder
