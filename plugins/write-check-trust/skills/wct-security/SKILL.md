---
name: wct-security
description: Run and interpret WCT static security, secret, dependency vulnerability, and SBOM checks. Use for security review, dependency upgrades, trust-boundary code, leaked credentials, or G-SAST, G-SECRET, G-CVE, and G-SBOM failures.
---

# Run security gates

Run `uv run bandit -q -r src tools/wct`, `uv run semgrep --config governance/semgrep`, `uv run detect-secrets scan --baseline .secrets.baseline`, and `uv run pip-audit`. Fix the root issue; never whitelist a finding without a narrow justification, owner, and issue. At trust boundaries retain validation even when minimalism suggests fewer lines.

