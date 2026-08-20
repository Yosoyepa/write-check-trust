---
name: wct-mutate
description: Run WCT differential mutation analysis and eliminate surviving mutants. Use after behavior changes, when coverage looks suspiciously easy, for G-MUT or G-MUT-SITES failures, and before hardening handoff.
---

# Harden with mutation

1. Run `uv run wct mutate scan`; split any changed file above 100 mutation sites for behavioral reasons.
2. Run `uv run wct mutate run`; the manifest selects changed functions.
3. For uncovered mutants, add a test that reaches the behavior. For survivors, strengthen assertions or simplify equivalent code.
4. Require zero survivors in changed code.
5. Only after green, run `uv run wct mutate update-manifest` and include the manifest with the verified change.

