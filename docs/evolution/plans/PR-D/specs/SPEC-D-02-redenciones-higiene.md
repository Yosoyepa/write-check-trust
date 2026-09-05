# SPEC-D-02 — Redenciones: F11-b, ruff extend, artefacto relativo (Coder-D2)

ADRs: [D-02](../decisions/ADR-D-02-f11b-vulture-60-whitelist.md),
[D-03](../decisions/ADR-D-03-ruff-extend.md),
[D-04](../decisions/ADR-D-04-artefacto-relativo.md).
Escenarios: [GHERKIN-D.md](../GHERKIN-D.md) (resto).

## Paso 0 (documentar en handoff)

1. Verifica el repro de la sonda: `uv run vulture src tools/wct
   --min-confidence 60` → exactamente 1 hallazgo (FP `abstract_symbols`).
   Documenta salida. Si aparece MÁS de 1, detente y repórtalo (hallazgo
   nuevo — no lo whitelistees).
2. Mapea los consumidores del campo `ir["source"]` del IR de aceptación
   (`tests/acceptance/steps.py`, `accept run`/`mutate`, artefacto
   generado): quién resuelve la ruta y contra qué. Documenta antes de
   cambiar la normalización.
3. Verifica el footgun: `uv run ruff check tools/wct/gate/checks.py`
   (sin `--config`) falla con I001 hoy; con `--config` pasa.

## Cambios

### 1. F11-b: vulture 60 + whitelist (ADR-D-02)

- `governance/thresholds.yaml`: `dead_code.vulture_min_confidence: 80` →
  `60`; clave nueva `dead_code.whitelist: governance/lint/vulture_whitelist.py`
  (con comentario de procedencia citando ADR-D-02 y la autorización
  delegada 2026-09-05).
- `governance/lint/vulture_whitelist.py` (nuevo): comentario de razón +
  la única entrada `abstract_symbols` (convención vulture: los nombres
  referenciados en la whitelist cuentan como usados).
- `tools/wct/gate/checks.py::dead_code_command`: añade
  `--whitelist <ruta>` SOLO cuando la clave existe (patrón PR-B: clave
  declarada; ausencia → sin flag, sin default silencioso).
- Conversión del caso: `quality/redteam/cases.yaml` pierde F11-b (y su
  comentario); `quality/redteam/cases-tool.yaml` gana
  `{id: F11-b, failure_mode: F11, harness: gate-tool, gate: G-DEAD,
  tool: vulture}` con comentario (adversario: constante muerta a
  confianza 60, umbral declarado en el fixture); builder `f11_b` en
  `tools/wct/selftest/fixtures_tools.py` (patrón f1_b: governance mínimo
  con `vulture_min_confidence: 60` + src con `UNUSED_CONSTANT = 7`).
- `tools/wct/selftest/redteam.py`: el reconocedor `unused` de `_reject`
  queda muerto (F11-b era su único usuario) — ELIMÍNALO.
- Tests: `tests/unit/test_redteam_tools.py` parametrizado gana F11-b (9
  casos); rojo primero.
- Verificación dura: `uv run vulture src tools/wct --min-confidence 60
  --whitelist governance/lint/vulture_whitelist.py` → **0 hallazgos**
  (baseline del ratchet intacta, sin `ratchet record`).

### 2. ruff extend (ADR-D-03)

- `pyproject.toml`: sección `[tool.ruff]` con
  `extend = "governance/lint/ruff.toml"`.
- Test TDD (rojo primero — hoy falla): subprocess `ruff check
  tools/wct/gate/checks.py` SIN `--config` → exit 0. Y test de no
  regresión: con `--config` sigue pasando.

### 3. Artefacto de aceptación relativo (ADR-D-04)

- Normaliza el `source` del IR a ruta relativa al root del repo cuando el
  feature vive bajo él (fallback: tal cual). Resuelve en el sitio
  correcto según el mapa del paso 0.2 — si `steps.py` u otro consumidor
  resolvía la ruta absoluta, ajústalo para resolver la relativa contra el
  root derivable en runtime.
- Test TDD: `generate` (o el nivel que fije el IR) desde DOS roots
  distintos produce artefactos byte-idénticos.
- Regenera `tests/acceptance/generated/test_acceptance.py` SOLO con
  `uv run wct accept generate`. El diff debe mostrar únicamente la ruta
  relativa — cualquier otra diferencia es hallazgo y se reporta (no se
  commitea).

## No hacer

- No tocar `tools/wct/report/**`, `tools/wct/gate/runner.py` (frontera
  D1). `checks.py` es tuyo SOLO en `dead_code_command`.
- No whitelistear nada beyond `abstract_symbols` sin evidencia.
- No editar artefactos generados a mano (TEST-009).
- No correr `ratchet record`, `integrity bless`, `mutate
  update-manifest`, push, ni PR.

## Commits

1. `feat(dead): vulture a confianza 60 con whitelist — redime F11-b` (por
   qué + autorización citada + salida de la sonda). `By coder.`
2. `fix(accept): el artefacto generado embebe ruta relativa` (repro de
   PR-C + test de dos roots + regeneración). `By coder.`
3. `chore(lint): ruff sin --config extiende el perfil del repo` (repro +
   test). `By coder.`
