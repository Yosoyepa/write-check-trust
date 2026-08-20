---
name: wct-test-honesty
description: Audit whether Python test assertions trace to production behavior. Use for weak or generated tests, mock-only assertions, suspicious coverage, test-suite review, or G-INTROVERT ratchet findings.
---

# Audit test honesty

1. Run `uv run wct introvert --json [test paths...]`.
2. Fix `introverted` first: assert an observable result derived from the SUT.
3. Treat `questionable` as “unknown”, not failure; inspect it manually.
4. Do not apply this heuristic to generated acceptance tests.
5. Keep it a ratchet, never a hard gate: static provenance is heuristic.

