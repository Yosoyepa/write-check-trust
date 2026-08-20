---
name: wct-hardening
description: Execute the full Uncle Bob-inspired WCT hardening sequence. Use for release readiness, hardener-role handoff, high-risk changes, or requests to fully validate code after implementation and architectural review.
---

# Perform hardening

Run strictly in this order and fix each stage before continuing:

1. `uv run wct mutate run`
2. `uv run wct accept mutate`
3. Generate LCOV and run `crap4py ... --max-crap 6`
4. `uv run wct dry --json`
5. `uv run wct gate --tier full`

Use at most eight mutation workers. Require zero survivors and report every optional gate that skipped.
