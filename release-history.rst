.. _release_history:

Release and Version History
==============================================================================


x.y.z (Backlog)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

**Minor Improvements**

**Bugfixes**

**Miscellaneous**


0.1.2 (2025-08-19)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Breaking Changes**

- **BREAKING**: Changed ``_shared`` to ``_defaults`` for configuration inheritance sections
    - All configuration files using ``_shared`` must be updated to use ``_defaults``
    - API constant renamed from ``SHARED`` to ``DEFAULTS``
    - This change improves semantic clarity by explicitly indicating these are default values
    - See migration guide in documentation for updating existing configurations

**Features and Improvements**

- Improved semantic clarity: ``_defaults`` better communicates the purpose of inheritance sections
- Enhanced documentation with clearer examples and explanations

**Minor Improvements**

- Updated all docstrings and examples to use ``_defaults`` terminology
- Improved error messages and function parameter names for consistency


0.1.1 (2025-08-17)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- First release
- Add the following public APIs:
    - ``configcraft.api.DEFAULTS``
    - ``configcraft.api.inherit_value``
    - ``configcraft.api.apply_inheritance``
    - ``configcraft.api.deep_merge``
