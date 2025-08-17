# -*- coding: utf-8 -*-

"""
Hierarchical Configuration Inheritance Pattern

This module provides a DRY (Don't Repeat Yourself) solution for configuration 
management by implementing inheritance patterns similar to object-oriented 
programming, but for JSON-like data structures.

**Problem It Solves**

When managing configurations for multiple environments (dev, staging, prod), 
you often need to repeat common settings across environments. This leads to 
duplication and maintenance overhead.

**Solution**

Use a special `_shared` section to define default values that automatically 
inherit to other sections, while allowing environment-specific overrides.

**How It Works**

The `_shared` section contains JSON path patterns that specify where default 
values should be applied. Values are only set if they don't already exist 
(no overwriting).

**Basic Example**

Input configuration::

    {
        "_shared": {
            "*.username": "root",        # Apply to all environments
            "*.memory": 2               # Default memory allocation
        },
        "dev": {
            "password": "dev123"        # Dev-specific setting
        },
        "prod": {
            "password": "prod456",      # Prod-specific setting
            "memory": 8                 # Override default memory
        }
    }

After applying inheritance, becomes::

    {
        "dev": {
            "username": "root",         # Inherited from _shared
            "password": "dev123",       # Original value
            "memory": 2                 # Inherited from _shared
        },
        "prod": {
            "username": "root",         # Inherited from _shared
            "password": "prod456",      # Original value
            "memory": 8                 # Override (not replaced)
        }
    }

**JSON Path Patterns**

- `*.field`: Apply to all top-level keys (except _shared)
- `env.field`: Apply to specific environment
- `*.db.*.port`: Apply to nested structures with wildcards
- `env.services.port`: Apply to specific nested path

**Key Features**

- Non-destructive: Existing values are never overwritten
- Recursive: Supports nested _shared sections for fine-grained control
- Flexible: Works with dictionaries and lists of dictionaries
- Order-aware: Evaluation order matters for overlapping patterns
"""

import typing as T

SHARED = "_shared"

_error_tpl = (
    "node at JSON path {_prefix!r} is not a dict or list of dict! "
    "cannot set node value '{prefix}.{key}' = ...!"
)


def make_type_error(prefix: str, key: str) -> TypeError:
    """
    Create a descriptive TypeError when trying to set a value on incompatible data types.
    
    This helper creates user-friendly error messages when the inheritance process 
    encounters data that isn't a dict or list of dicts, which are the only 
    structures that support key assignment.
    
    Args:
        prefix: The JSON path prefix where the error occurred
        key: The key we were trying to set
        
    Returns:
        TypeError with descriptive message about the invalid operation
    """
    if prefix == "":
        _prefix = "."
    else:
        _prefix = prefix
    return TypeError(_error_tpl.format(_prefix=_prefix, prefix=prefix, key=key))


def inherit_value(
    path: str,
    value: T.Any,
    data: T.Union[T.Dict[str, T.Any], T.List[T.Dict[str, T.Any]]],
    _prefix: T.Optional[str] = None,
):
    """
    Set a default value at a specific JSON path, but **only if it doesn't already exist**.
    
    This is the core inheritance mechanism that applies a single shared value to 
    its target location(s) in the configuration data. It navigates through nested 
    structures using dot notation and wildcards, but never overwrites existing values.
    
    **What it does:**
    - Follows JSON path patterns like "*.username" or "dev.database.port"
    - Sets values only where they're missing (non-destructive)
    - Handles wildcards (*) to apply to multiple targets
    - Works with nested dicts and lists of dicts
    
    **Examples:**
    - Path "*.memory" → Sets memory=2 in all top-level environments
    - Path "dev.db.port" → Sets port=5432 only in dev.db
    - Path "*.servers.*.cpu" → Sets cpu=1 in all servers across all environments
    
    Args:
        path: JSON path pattern (e.g., "*.username", "dev.db.port")
        value: The default value to set
        data: Configuration dict/list to modify in-place
        _prefix: Internal recursion parameter (do not use)
        
    Raises:
        ValueError: If path ends with "*" (incomplete path)
        TypeError: If trying to set values on incompatible data types
    """
    if path.endswith("*"):
        raise ValueError("json path cannot ends with *!")
    if _prefix is None:
        _prefix = ""

    parts = path.split(".")

    if len(parts) == 1:
        if isinstance(data, dict):
            data.setdefault(parts[0], value)
        elif isinstance(data, list):
            for item in data:
                if not isinstance(item, dict):
                    raise make_type_error(_prefix, parts[0])
                item.setdefault(parts[0], value)
        else:
            raise make_type_error(_prefix, parts[0])
        return

    key = parts[0]
    if key == "*":
        for k, v in data.items():
            if k != SHARED:
                inherit_value(
                    path=".".join(parts[1:]),
                    value=value,
                    data=v,
                    _prefix=f"{_prefix}.{key}",
                )
    else:
        if isinstance(data, dict):
            inherit_value(
                path=".".join(parts[1:]),
                value=value,
                data=data[key],
                _prefix=f"{_prefix}.{key}",
            )
        elif isinstance(data, list):
            for item in data:
                inherit_value(
                    path=".".join(parts[1:]),
                    value=value,
                    data=item[key],
                    _prefix=f"{_prefix}.{key}",
                )
        else:
            raise make_type_error(_prefix, key)


def apply_inheritance(data: dict):
    """
    Transform configuration data by applying all ``_shared`` inheritance rules.
    
    This is the main entry point that processes an entire configuration structure,
    finding all _shared sections and applying their inheritance rules to create
    the final resolved configuration.
    
    **What it does:**
    1. Recursively processes nested _shared sections (deeper ones override shallower ones)
    2. Applies each JSON path pattern in the _shared section
    3. Removes all _shared sections from the final output
    4. Modifies the input data in-place
    
    **Example:**
    Input::
    
        {
            "_shared": {"*.memory": 2},
            "dev": {},
            "prod": {"memory": 8}
        }
    
    Output::
    
        {
            "dev": {"memory": 2},     # Inherited default
            "prod": {"memory": 8}     # Kept existing value
        }
    
    Args:
        data: Configuration dictionary with _shared sections to process
        
    Note:
        Modifies the input dictionary in-place. After calling this function,
        all _shared sections will be removed and their rules applied.
    """
    # implement recursion pattern
    for key, value in data.items():
        if key == SHARED:
            continue
        if isinstance(value, dict):
            apply_inheritance(value)
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    apply_inheritance(item)

    # try to set shared value
    has_shared = SHARED in data
    if has_shared is False:
        return

    # pop the shared data, it is not needed in the final result
    shared_data = data.pop(SHARED)
    for path, value in shared_data.items():
        inherit_value(path=path, value=value, data=data)
