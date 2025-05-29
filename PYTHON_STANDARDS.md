# Python Code Standards

This document outlines the coding standards and best practices for Python development in this project.

## Code Style

- Follow [PEP 8](https://peps.python.org/pep-0008/) style guide for Python code
- Use 4 spaces for indentation (no tabs)
- Maximum line length of 88 characters (Black formatter default)
- Use meaningful variable and function names that reflect their purpose
- Use snake_case for variables and functions
- Use PascalCase for class names

## Function and Class Guidelines

1. **Function Design**
   - Keep functions focused on a single responsibility
   - Extract complex logic into separate, well-named functions
   - Add descriptive docstrings to all functions explaining parameters and return values
   - Maximum function length should be around 50 lines (use your judgment)

2. **Class Design**
   - Group related functions into classes when appropriate
   - Follow the Single Responsibility Principle
   - Use inheritance sparingly and prefer composition
   - Document class purpose and attributes in docstrings

## Documentation

- Add docstrings to all modules, classes, and functions
- Use Google-style docstring format:
  ```python
  def function_name(param1: type, param2: type) -> return_type:
      """Short description of the function.

      Args:
          param1: Description of param1
          param2: Description of param2

      Returns:
          Description of return value

      Raises:
          ExceptionType: Description of when this exception is raised
      """
  ```

## Error Handling

- Use specific exception types instead of catching all exceptions
- Add appropriate error handling for edge cases
- Include meaningful error messages
- Use custom exceptions when appropriate

## Testing

- Write unit tests for all new functionality
- Use pytest as the testing framework
- Aim for high test coverage
- Include both positive and negative test cases
- Mock external dependencies in tests

## Code Organization

- Group related functionality into modules
- Use `__init__.py` files appropriately
- Keep the project structure clean and logical
- Use absolute imports instead of relative imports

## Dependencies

- Document all dependencies in `requirements.txt`
- Pin dependency versions
- Use virtual environments for development
- Keep dependencies up to date and secure

## Tools

We use the following tools to maintain code quality:

- **Black**: Code formatter
- **isort**: Import sorter
- **flake8**: Linter
- **mypy**: Static type checker
- **pytest**: Testing framework

## Pre-commit Hooks

We use pre-commit hooks to automatically:
- Format code with Black
- Sort imports with isort
- Run flake8 checks
- Run mypy type checking
- Run pytest

## Getting Started

1. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

2. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

3. Run tests:
   ```bash
   pytest
   ```

## Code Review Process

1. All code changes must be reviewed before merging
2. Ensure all tests pass
3. Verify code style compliance
4. Check for proper documentation
5. Review error handling
6. Consider performance implications 