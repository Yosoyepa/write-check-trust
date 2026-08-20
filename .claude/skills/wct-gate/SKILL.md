---
name: wct-gate
description: Run and interpret WCT quality tiers. Use for pre-handoff checks, failing CI, selecting fast versus commit versus full verification, or fixing a named G-* gate without weakening policy.
---

# Run WCT gates

1. Run `uv run wct gate --tier fast` while editing, `--tier commit` before handoff, and `--tier full` before release.
2. Treat `FAIL` and `ERROR` as blocking. Treat `SKIP` as visible missing coverage, never as proof.
3. Fix production code or tests. Do not edit thresholds, baselines, generated rules, or integrity locks to obtain green.
4. Rerun the smallest failing command, then rerun the original tier.
5. Report every skipped gate and the reason.

