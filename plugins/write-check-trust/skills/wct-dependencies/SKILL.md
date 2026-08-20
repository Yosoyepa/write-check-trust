---
name: wct-dependencies
description: Audit Python dependencies and import contracts. Use for adding or removing packages, dependency bloat, missing or transitive imports, import cycles, G-DEPS failures, or deciding whether an installed dependency is architecture-safe.
---

# Audit dependencies

1. Search the codebase and standard library before adding a package.
2. Run `uv run deptry .` and `uv run lint-imports`.
3. Declare every direct dependency and remove unused declarations.
4. Never use an installed framework dependency in domain/application when policy forbids it.
5. Rerun `uv lock` and vulnerability checks after dependency changes.

