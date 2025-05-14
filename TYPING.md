# Type Checking Strategy

## Current Status

The project is in the process of adding type annotations to improve code quality and catch errors early. Currently, we have:

- Basic mypy configuration in `mypy.ini`
- A custom script (`scripts/run_mypy.py`) that handles Python version compatibility issues
- Relaxed type checking settings to allow for gradual adoption

## Type Checking Issues

The current codebase has several type checking issues:

1. Missing type annotations for functions and variables
2. Incompatible return value types
3. Import and attribute errors
4. Redefined names

## Gradual Adoption Strategy

We're taking a gradual approach to adding type annotations:

1. **Phase 1 (Current)**: Run mypy with relaxed settings to identify issues without blocking CI
2. **Phase 2**: Add type annotations to core modules, starting with:
   - `src/utils/`
   - `src/llm/provider.py`
   - `src/llm/question_generator.py`
3. **Phase 3**: Add type annotations to PDF generation modules
4. **Phase 4**: Add type annotations to tests
5. **Phase 5**: Enable stricter type checking in mypy configuration

## How to Contribute Type Annotations

When adding type annotations:

1. Focus on function signatures first (parameters and return types)
2. Use appropriate types from the `typing` module (`List`, `Dict`, `Optional`, etc.)
3. Add variable annotations for complex types
4. Run `python scripts/run_mypy.py` locally to check your changes

Example:

```python
from typing import List, Dict, Optional

def process_data(items: List[str], config: Optional[Dict[str, str]] = None) -> List[str]:
    """Process a list of items according to the config."""
    results: List[str] = []
    # Implementation
    return results
```

## Special Cases

- **Python 3.10 Compatibility**: We skip mypy for Python 3.10 due to pydantic compatibility issues
- **Pydantic**: We have special handling for pydantic in our mypy configuration 