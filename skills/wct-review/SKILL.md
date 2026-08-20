---
name: wct-review
description: Review code and diffs against WCT architecture, minimalism, testing, dependency, and security policy. Use for code review, pull-request review, agent handoff review, or investigating whether a passing change still violates human-only rules.
---

# Review hardened code

1. Read `governance/policy.yaml`, `thresholds.yaml`, and the relevant files under `governance/rules/`.
2. Inspect the complete changed flow and every caller before judging the diff.
3. Run `uv run wct gate --tier commit` and `uv run wct dry --json`.
4. Check rules marked `verified_by: [human]` explicitly: semantic correctness, information hiding, names, accessibility, and root cause.
5. Lead with concrete findings ordered by severity and include file/line evidence. Do not rewrite code unless asked.

