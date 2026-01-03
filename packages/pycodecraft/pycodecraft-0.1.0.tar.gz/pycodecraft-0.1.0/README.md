# CodeCraft 🏗️

<div align="center">

**A Pythonic library for programmatic code generation using elegant context managers**

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[Features](#-features) •
[Installation](#-installation) •
[Quick Start](#-quick-start) •
[Documentation](#-documentation) •
[Examples](#-examples)

</div>

---

## ✨ Features

- **🎯 Intuitive Context Manager API** - Natural, Pythonic code generation
- **📦 Full Python Support** - Classes, functions, decorators, control flow, and more
- **🔄 Smart Import Management** - Automatic deduplication and conditional imports
- **🎨 Automatic Formatting** - Built-in indentation and optional Black integration
- **✅ Syntax Validation** - Compile-time validation of generated code
- **🏗️ Type-Safe** - Full type hints support
- **🚀 Production Ready** - Battle-tested with comprehensive test coverage

## 📦 Installation

```bash
pip install codecraft
```

Or install from source:

```bash
git clone https://github.com/yourusername/codecraft.git
cd codecraft
pip install -e .
```

## 🚀 Quick Start

```python
from codecraft import CodeBuilder

with CodeBuilder() as code:
    code.add_import("dataclasses", ["dataclass"])

    with code.class_("User", decorators=["@dataclass"]):
        code.docstring("Represents a user in the system.")
        code.attr("name", "str")
        code.attr("email", "str")
        code.attr("age", "int | None", default="None")

        with code.method("greet", returns="str"):
            code.docstring("Returns a greeting message.")
            code.return_('f"Hello, {self.name}!"')

print(code.generate())
```

**Output:**

```python
from dataclasses import dataclass


@dataclass
class User:
    """Represents a user in the system."""
    name: str
    email: str
    age: int | None = None

    def greet(self) -> str:
        """Returns a greeting message."""
        return f"Hello, {self.name}!"
```

## 📚 Documentation

### Core Concepts

#### CodeBuilder

The main entry point for code generation. Use it as a context manager:

```python
with CodeBuilder() as code:
    # Your code generation here
    pass

result = code.generate()
```

#### Context Managers

Create Python structures using intuitive context managers:

```python
# Classes
with code.class_("MyClass", bases=["BaseClass"], decorators=["@decorator"]):
    code.attr("x", "int")

# Functions
with code.function("my_func", params=["x: int", "y: str"], returns="bool"):
    code.line("return True")

# Methods (auto-adds 'self')
with code.method("process", params=["data: dict"], returns="None"):
    code.line("self.data = data")

# Control Flow
with code.if_("condition"):
    code.line("do_something()")
with code.elif_("other_condition"):
    code.line("do_other()")
with code.else_():
    code.line("do_default()")

# Loops
with code.for_("item", "items"):
    code.line("process(item)")

with code.while_("running"):
    code.line("tick()")

# Exception Handling
with code.try_():
    code.line("risky_operation()")
with code.except_("ValueError", "e"):
    code.line("handle_error(e)")
with code.finally_():
    code.line("cleanup()")

# Context Managers
with code.with_("open('file.txt')", "f"):
    code.line("data = f.read()")
```

#### Direct Operations

```python
# Add lines of code
code.line("x = 10")
code.line("y = 20")

# Add blank lines
code.blank_line()
code.blank_lines(3)  # Add 3 blank lines

# Add comments
code.comment("This is a comment")

# Add docstrings (context-aware)
code.docstring("Module-level docstring")

# Add return statements
code.return_("result")

# Raw code (no indentation)
code.raw("#!/usr/bin/env python3")
```

#### Import Management

```python
# Simple import
code.add_import("os")
code.add_import("sys")

# From import
code.add_from_import("typing", ["List", "Dict", "Optional"])

# Automatic deduplication
code.add_import("os")  # Won't duplicate

# Conditional imports (inside contexts)
with code.if_("TYPE_CHECKING"):
    code.add_import("mypy_extensions", ["TypedDict"])  # Added as code line, not global import
```

### Advanced Features

#### Async Support

```python
with code.function("fetch_data", async_=True, returns="dict"):
    code.line("data = await api.get()")
    code.return_("data")
```

#### Nested Structures

```python
with code.class_("Outer"):
    with code.class_("Inner"):
        code.attr("value", "int")

    with code.method("create_inner", returns="Inner"):
        code.return_("self.Inner()")
```

#### Code Validation

```python
# Simple validation
is_valid = code.validate()  # Returns bool

# Detailed validation
result = code.validate(detailed=True)
# Returns: {"valid": True, "errors": [], "warnings": []}
```

#### Save to File

```python
# Save with optional formatting
code.save("output.py", format=True, line_length=88)
```

## 💡 Examples

### Example 1: FastAPI Endpoint

```python
from codecraft import CodeBuilder

with CodeBuilder() as code:
    code.add_from_import("fastapi", ["FastAPI", "HTTPException"])
    code.add_from_import("pydantic", ["BaseModel"])
    code.blank_line()

    code.line("app = FastAPI()")
    code.blank_lines(2)

    with code.class_("UserCreate", bases=["BaseModel"]):
        code.attr("username", "str")
        code.attr("email", "str")

    code.blank_lines(2)

    with code.function("create_user",
                       params=["user: UserCreate"],
                       returns="dict",
                       decorators=["@app.post('/users')"]):
        with code.if_("user.username in existing_users"):
            code.line('raise HTTPException(400, "User exists")')
        code.return_("{'id': new_id, 'username': user.username}")

print(code.generate())
```

### Example 2: Data Processing Function

```python
from codecraft import CodeBuilder

with CodeBuilder() as code:
    with code.function("process_items", params=["items: list"], returns="list"):
        code.line("results = []")
        code.blank_line()

        with code.for_("item", "items"):
            with code.try_():
                code.line("processed = item.process()")

                with code.if_("processed.is_valid()"):
                    code.line("results.append(processed)")
                with code.else_():
                    code.line('print(f"Invalid: {item}")')

            with code.except_("Exception", "e"):
                code.line('print(f"Error: {e}")')

        code.blank_line()
        code.return_("results")

print(code.generate())
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=codecraft --cov-report=html

# Run specific test file
pytest tests/test_core/test_builder.py -v
```

## 🛣️ Roadmap

- [x] Core API with context managers
- [x] Class and function generation
- [x] Control flow structures
- [x] Import management
- [x] Code validation
- [ ] Advanced operations (find, modify, remove)
- [ ] Template system
- [ ] CLI tool
- [ ] Type stub generation (`.pyi` files)
- [ ] Full Black formatter integration

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by the need for clean, maintainable code generation
- Built with modern Python best practices
- Designed for developer happiness

---

<div align="center">

**Made with ❤️ by [victorgabrieldeon](https://github.com/victorgabrieldeon)**

⭐ Star this repo if you find it useful!

</div>
