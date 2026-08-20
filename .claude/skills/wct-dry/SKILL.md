---
name: wct-dry
description: Detect fuzzy structural duplication with normalized Python AST fingerprints and extraction pressure. Use for duplication review, generated boilerplate, G-DRY failures, or deciding whether similar code should be extracted or deliberately remain separate.
---

# Detect structural duplication

1. Run `uv run wct dry --json [paths...]`.
2. Interpret Jaccard score >= 0.82 as a candidate, not an automatic refactor.
3. Act only on `ai_actionability: EXTRACT`; inspect `variation_points` and `extraction_pressure` first.
4. Preserve small test case matrices; repeated test shape can encode useful coverage.
5. Prefer deletion or reuse of an existing function over introducing a new generic helper.

