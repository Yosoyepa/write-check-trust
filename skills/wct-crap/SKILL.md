---
name: wct-crap
description: Measure and reduce Change Risk Anti-Pattern scores by combining cyclomatic complexity with branch coverage. Use for CRAP reports, risky-function triage, pre-refactor characterization, or failures of G-CRAP.
---

# Reduce CRAP risk

1. Generate LCOV: `uv run pytest --cov --cov-branch --cov-report=lcov:build/coverage/lcov.info`.
2. Run `uv run crap4py src --lcov build/coverage/lcov.info --max-crap 6`.
3. Start with the highest score. Add behavior-focused characterization tests before refactoring.
4. Reduce branches or add meaningful branch coverage; never split mechanically only to game CC.
5. Keep changed functions at CRAP <= 6. Never raise the threshold.

Formula: `CC² × (1 − coverage)³ + CC`.

