# Architecture Overview

## Design Principles

1. **Single Responsibility**: Each checker handles one validation concern
2. **Open/Closed**: Easy to add new checkers without modifying existing code
3. **Dependency Inversion**: Checkers depend on abstractions, not concrete implementations

## Module Structure
```
unity_validator/
├── core/           # Framework and base classes
├── checkers/       # Validation implementations
├── operators/      # Blender operators
├── ui/             # User interface
└── utils/          # Utilities and helpers
```

## Key Components

### BaseChecker (Abstract Base Class)

All checkers inherit from `BaseChecker` and implement the `check()` method.
```python
class BaseChecker(ABC):
    name: str
    description: str
    default_severity: Severity
    
    @abstractmethod
    def check(self, obj: bpy.types.Object) -> List[ValidationResult]:
        pass
```

### Registry Pattern

Checkers are registered using a decorator:
```python
@register_checker
class TransformChecker(BaseChecker):
    ...
```

### ValidationResult

Standardized result format for all checkers:
```python
@dataclass
class ValidationResult:
    checker_name: str
    severity: Severity
    object: bpy.types.Object
    message: str
    details: dict
```

## Version Compatibility

The `utils/compat.py` module provides version-agnostic APIs:
```python
# Instead of directly accessing mesh.use_auto_smooth
has_auto_smooth(mesh)  # Works on 3.6 - 4.2+
```

## Extension Guide

To add a new checker:

1. Create a new file in `checkers/`
2. Inherit from `BaseChecker`
3. Implement `check()` method
4. Add `@register_checker` decorator

The checker will automatically appear in the UI.