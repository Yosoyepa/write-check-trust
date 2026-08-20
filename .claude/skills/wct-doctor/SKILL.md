---
name: wct-doctor
description: Diagnose WCT installation, generated-rule drift, hook wiring, integrity locks, Python tooling, and forbidden minimalism modes. Use when hooks appear silent, gates cannot start, provider rules are stale, or the harness itself may be bypassed.
---

# Diagnose WCT

Run `uv run wct doctor`. Fix every FAIL in order: configuration, Python/uv, generated rules, hook events, integrity lock, then required executables. A crashing guard is blocking by design; do not convert errors to skips. Validate again with `uv run wct selftest redteam`.

