# Coding Standards

To ensure a production-ready codebase, all contributors must adhere to the following standards:

## Python
1. **Formatting**: All code must be formatted using `black`.
2. **Linting**: Code must pass `flake8` without warnings.
3. **Type Hinting**: Extensive use of Python `typing` is required for all functions and class methods.
    ```python
    def calculate_distance(x1: int, y1: int, x2: int, y2: int) -> float:
        pass
    ```
4. **Docstrings**: Use Google-style docstrings for all public classes and methods.
5. **Naming Conventions**:
    - Variables/Functions/Methods: `snake_case`
    - Classes: `PascalCase`
    - Constants: `UPPER_SNAKE_CASE`

## JavaScript / Web
1. **Formatting**: Use `Prettier`.
2. **Linting**: Use `ESLint` with strict configurations.
3. **Naming Conventions**:
    - Variables/Functions: `camelCase`
    - Classes/Components: `PascalCase`
    - DOM IDs/Classes: `kebab-case`

## JSON Levels
- Level files must be named `level001.json`, `level002.json`, etc.
- Keys should be `camelCase`.
