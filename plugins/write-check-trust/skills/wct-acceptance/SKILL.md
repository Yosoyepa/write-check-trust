---
name: wct-acceptance
description: Build and verify WCT's Python-native Gherkin acceptance pipeline. Use for feature specifications, scenario outlines, generated acceptance tests, IR duplication, hardcoded examples, G-ACCEPT failures, or acceptance mutation.
---

# Verify acceptance behavior

1. Write deterministic externally observable behavior in `features/*.feature`.
2. Run `uv run wct accept parse <feature>` then `uv run wct accept ir-dry <feature>`.
3. Reuse regex-shaped step handlers for wording that differs only by values.
4. Run `uv run wct accept generate <feature>` and `uv run wct accept run <feature>` sequentially.
5. Run `uv run wct accept mutate <feature>` and require zero surviving example-value mutations.

