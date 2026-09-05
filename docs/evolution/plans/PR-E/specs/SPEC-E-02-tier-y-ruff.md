# SPEC-E-02 — G-MUT al tier full + root-cause ruff desnudo (Coder-E2)

ADRs: [E-02](../decisions/ADR-E-02-gmut-full-tier.md).
Escenarios: [GHERKIN-E.md](../GHERKIN-E.md) (wct-gmut-full-001).

## Paso 0 (documentar en handoff)

1. Mide `mutmut run` frío (sin cache: borra `.mutmut-cache`/`mutants/`
   antes) sobre el repo — el número para el presupuesto del tier. Y el
   tier full completo con G-MUT dentro (antes/después).
2. ruff: compara los settings efectivos de `ruff check .` (desnudo, con
   el `extend` activo) vs `--config governance/lint/ruff.toml` —
   `uv run ruff check --show-settings .` en ambas formas; encuentra la
   clave que difiere (hipótesis: per-file-ignores no se están aplicando
   en modo extend). Documenta la causa raíz con la salida.

## Cambios

### 1. `tools/wct/gate/runner.py` — TIERS["full"] gana "G-MUT"

Una línea en la lista del tier full (después de G-COV-TOTAL, antes de
los DRY — o donde el orden del tier tenga sentido: mutación después de
que la suite ya pasó). El perfil de capacidades lo refleja solo (tiers
derivados). Si el hallazgo del paso 0 de E1 exige cierre del contrato
exit-code, NO lo implementes tú — es frontera de revisión (repórtalo).

### 2. Tests

- TDD: test que fija `G-MUT in TIERS["full"]` y `G-MUT not in` los demás
  tiers (rojo primero).
- Test de presupuesto: el runtime NO se aserta en test (frágil) — se
  mide y reporta en el handoff; el test fija membresía, no milisegundos.

### 3. `docs/STATUS.md`

Actualiza el conteo del tier full (33 → 34) y la fila del kit de
verificación si menciona G-MUT como suelto.

### 4. ruff desnudo — fix condicional

- Si el root-cause admite fix quirúrgico (≤5 líneas, en pyproject.toml
  `[tool.ruff]` — protegido, autorizado por la delegación vigente — o
  corrigiendo el patrón de per-file-ignores en governance/lint/ruff.toml
  si ESA es la causa): aplícalo con test (ruff desnudo sobre el árbol →
  0 hallazgos; rojo primero: hoy 622) y addendum fechado en
  ADR-D-03 del dossier PR-D (docs/evolution/plans/PR-D/decisions/).
- Si el root-cause es estructural (semántica de extend que no puede
  cargar per-file-ignores): NO fuercen nada — documenta el hallazgo en
  el handoff con la salida de --show-settings; el arquitecto decide.

## No hacer

- No tocar selftest/**, quality/redteam/**, tests/unit/test_redteam_tools
  (frontera E1).
- No cablear G-MUT a pr/fast/commit (ADR-E-02 alternativa (b) diferida).
- No cambiar scope/thresholds de mutación.

## Commit

`feat(gate): G-MUT se une al tier full con mutacion real en el ejemplo`
(+ el de ruff si aplica: `fix(lint): ruff desnudo aplica per-file-ignores
del perfil`). Byline `By coder.`
