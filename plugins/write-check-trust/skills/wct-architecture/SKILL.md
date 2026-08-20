---
name: wct-architecture
description: Enforce WCT dependency direction, forbidden imports, cycles, fan-in/fan-out, Instability, Abstractness, Distance, and architecture zones. Use for architecture review, module moves, new dependencies, G-ARCH failures, or framework leakage into core layers.
---

# Enforce architecture

1. Run `uv run lint-imports` for declared contracts.
2. Run `uv run wct archmetrics --json` for cycles and A/I/D metrics.
3. Keep dependencies pointing inward: entrypoints -> adapters -> application -> domain.
4. Define ports in the consuming high-level layer. Keep framework and persistence types outside domain/application.
5. Treat new pain/useless zones as regressions; do not inflate Abstractness through configuration.

