# PR-F — ANALYSIS (evidencia medida, 2026-09-05)

## El residuo y su declaración

- `quality/redteam/cases.yaml:12` — F4-b declarado heurístico con razón in
  situ: *"diff-cover exige fixture git con rama base y diff real; factible
  pero frágil. Redención: candidato a PR-C2 pequeño si la demanda lo
  justifica"*. Es el único `harness: heuristic` que queda (F9-b redimido en
  PR #31, F11-b en PR-D).
- Línea base del red team (medida hoy): `30/30 rechazados · 13 gate-engine ·
  12 gate-tool · 4 hook · 1 heuristic (declarados) · 0 SKIP`.
- El feature `wct-redteam-residual-001` existe SOLO para declarar residuos;
  su Examples tiene la única fila F4-b.

## Contrato del gate productivo (leído en código, no adivinado)

- `tools/wct/gate/runner.py:124-158` `gate_coverage_diff`:
  1. `shutil.which("diff-cover")` ausente → ERROR (no SKIP).
  2. `remote_base(root)` → base del diff; None → ERROR.
  3. `coverage_diff_command(root, base)` → None → FAIL nombrando
     `coverage.diff_min`.
  4. `_captured(root, command)` → exit≠0 → **FAIL** (`gate/exec.py:19-21`).
- `tools/wct/util/git.py:52-66` `remote_base`: candidatos `origin/$GITHUB_BASE_REF`,
  `origin/main`, `origin/master`, `main`, `master` — el primero que
  `git rev-parse --verify` resuelva. Un repo local con `main` commiteada
  resuelve `"main"` (sin remote, las candidatas `origin/*` fallan primero).
- `tools/wct/gate/checks.py:120-137` `coverage_diff_command`:
  `diff-cover build/coverage/lcov.info --compare-branch <base> --fail-under
  <diff_min> --include-untracked`, ejecutado con `cwd=root` del fixture.
  `diff_min` productivo = **90** (`governance/thresholds.yaml:113`).
- `tools/wct/gate/checks.py:85-98` `_declared` → `load_config(root)` exige
  `governance/policy.yaml` y `governance/thresholds.yaml` legibles con
  `schema_version: 1` (mismo convenio que `_vulture_governance`,
  `fixtures_tools.py:246-255`).
- diff-cover **10.5.1** presente en el venv (`.venv/bin/diff-cover`) y en CI
  (G-COV-DIFF pasa en tier commit, 20/20).

## Sonda del fixture (paso 0, `build/tmp/probe_f4b.py`, corrida sin pipes)

Fixture: `git init -b main` → gobernanza mínima (`policy.yaml` +
`thresholds.yaml` con `coverage.diff_min: 90`) → `git add -A` → commit base
(con `-c user.email/-c user.name/-c commit.gpgsign=false`) → víctima
`src/victim/ops.py` (`def add` en 2 líneas) → `build/coverage/lcov.info` con
`DA:1,0` y `DA:2,0`.

| variante | estado del fixture | veredicto del gate productivo |
|---|---|---|
| A — víctima untracked | sin rama extra | **FAIL** · `Coverage: 0%` · `Failure. Coverage is below 90%.` |
| B — víctima commiteada en rama `feature` | `main` vs `feature` | **FAIL** · `Coverage: 0%` · `Failure. Coverage is below 90%.` |

Ambas cazan. Se elige **A**: menos estado (3 comandos git), y ejercita el
flag productivo `--include-untracked` — cuyo propósito exacto es "archivo
nuevo aún no commiteado", que ES el escenario F4-b (producción nueva, sin
tests). Ver ADR-F-01.

## Presupuestos y colaterales

- `tools/wct/selftest/fixtures_tools.py`: **426/500 LOC** (74 de margen; el
  builder entra sin partir el archivo). `redteam.py`: 242/500 (y el retiro
  del checker lo reduce).
- Precedente git en fixtures: `_git_track` (`fixtures_tools.py:284-288`)
  hace `git init` + `git add` para detect-secrets; F4-b añade el commit base
  (necesario para que `main` resuelva en `rev-parse --verify`).
- Tests existentes que fijan el comportamiento a cambiar:
  - `tests/unit/test_redteam_tools.py:36-42` — parametrizado sobre
    `cases-tool.yaml` + `BUILDERS`: añadir el caso + builder lo ejercita
    automáticamente (aserción sobre el `GateResult` del gate productivo,
    TEST-003 ✓). `tmp_path` de pytest vive fuera del repo → el fixture git
    es visible para diff-cover.
  - `tests/unit/test_redteam_engine.py` — YAML sintético con `checker:
    testless` (casos R1, X5, X6): al retirar el checker hay que re-enfocar
    esos casos sintéticos a checkers reales (protected-write /
    forbidden-command).
- `GITHUB_BASE_REF` en CI solo añade una candidata `origin/<base>` que
  falla primero en el fixture (sin remote) — `remote_base` cae a `main`.
  Medido en la sonda local (sin la variable) y válido en CI por construcción
  del orden de candidatos (`util/git.py:63-66`).
- Invariario de modos: F4 conserva 2 casos en la unión (F4-a en
  `cases-engine.yaml:11`, F4-b migrado a `cases-tool.yaml`).
