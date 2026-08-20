---
name: wct-adopt
description: Adopt WCT (Write, Check, Trust) in an existing Python repository using strict-on-diff gates and measured whole-repository ratchets. Use for migration, template installation, initial baselining, provider adapter generation, or introducing hardening without requiring an immediate rewrite.
---

# Adopt WCT

1. Inventory language, source roots, tests, framework boundaries, and existing CI.
2. Copy the harness without overwriting project behavior.
3. Configure architecture layers and forbidden externals in `governance/policy.yaml`.
4. Measure existing metrics into baselines; do not invent favorable values.
5. Keep strict thresholds on changed code and ratchets on untouched legacy code.
6. Build provider rules, create the integrity lock, run doctor, then run commit tier.

