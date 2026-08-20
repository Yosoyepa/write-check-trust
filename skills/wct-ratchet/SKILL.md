---
name: wct-ratchet
description: Inspect WCT quality baselines and prevent metric regression. Use for legacy-repository adoption, suppression or debt growth, coverage changes, architecture-zone changes, and any temptation to edit governance/baselines to pass CI.
---

# Protect quality ratchets

1. Compare the current metric with `governance/baselines/<metric>.json` using its declared direction.
2. Improve the code until it meets or beats the baseline.
3. Never hand-edit a baseline. A legitimate exception requires human approval, an integrity blessing, reason, owner, and audit log.
4. Changed code still uses strict thresholds even when the repository profile is legacy.

